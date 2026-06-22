from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
import logging
import io
from data_repository import get_repository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "HO_Ticket_Tracker.xlsx")
CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL', 300))
DELETE_CODE = "1947"

# Get repository instance
repository = get_repository(EXCEL_PATH, CACHE_TTL_SECONDS)

logger.info(f"App initialized with cache TTL: {CACHE_TTL_SECONDS}s")

@app.route("/")
def index():
    """Serve the dashboard HTML."""
    return send_file(os.path.join(os.path.dirname(__file__), "dashboard.html"))


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    Get paginated list of all tasks.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 500)
    
    Response includes pagination metadata.
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = min(500, max(1, int(request.args.get("page_size", 50))))
        
        result = repository.get_tasks(page=page, page_size=page_size)
        logger.info(f"GET /api/tasks page={page} page_size={page_size}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_tasks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Create a new task."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        now = datetime.now()
        data["Date"] = now.strftime("%Y-%m-%d")
        data["Time Opened"] = now.strftime("%H:%M:%S")
        data["Last Modified"] = now.strftime("%Y-%m-%d %H:%M:%S")
        
        ticket_no = repository.save_task(data)
        logger.info(f"Created task {ticket_no}")
        return jsonify({"success": True, "ticket_no": ticket_no}), 201
    except Exception as e:
        logger.error(f"Error in add_task: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/tasks/<ticket_no>", methods=["PUT"])
def update_task(ticket_no: str):
    """Update an existing task."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        data["Ticket No"] = ticket_no
        data["Last Modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        repository.save_task(data, ticket_no=ticket_no)
        logger.info(f"Updated task {ticket_no}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error in update_task: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/verify-delete-code", methods=["POST"])
def verify_delete_code():
    """Verify deletion code."""
    try:
        data = request.json or {}
        code = data.get("code", "").strip()
        is_valid = code == DELETE_CODE
        return jsonify({"valid": is_valid})
    except Exception as e:
        logger.error(f"Error in verify_delete_code: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/tasks/<ticket_no>", methods=["DELETE"])
def delete_task(ticket_no: str):
    """Delete a task (requires verification code)."""
    try:
        data = request.json or {}
        code = data.get("code", "").strip()
        
        if code != DELETE_CODE:
            return jsonify({"success": False, "error": "Invalid code. Task cannot be deleted."}), 403
        
        if repository.delete_task(ticket_no):
            logger.info(f"Deleted task {ticket_no}")
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Task not found"}), 404
    except Exception as e:
        logger.error(f"Error in delete_task: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/download", methods=["GET"])
def download_filtered():
    """
    Export filtered tasks as styled Excel file.
    
    Query parameters:
    - status: Filter by status ("open", "closed", or blank)
    - dept: Filter by department/vendor
    - employee: Filter by assigned employee
    - priority: Filter by priority
    - search: Search term (supports #ticketnumber syntax)
    """
    try:
        status_filter = request.args.get("status", "open")
        dept_filter = request.args.get("dept", "")
        employee_filter = request.args.get("employee", "")
        priority_filter = request.args.get("priority", "")
        search_filter = request.args.get("search", "")
        
        df = repository.load_dataframe()
        filtered = repository.search_tasks(
            df=df,
            search_term=search_filter,
            status_filter=status_filter,
            vendor_filter=dept_filter,
            employee_filter=employee_filter,
            priority_filter=priority_filter
        )
        
        excel_bytes = repository.export_to_excel(
            filtered,
            status_filter=status_filter,
            dept_filter=dept_filter,
            employee_filter=employee_filter,
            priority_filter=priority_filter
        )
        
        filename_parts = ["Tasks"]
        if status_filter == "open":
            filename_parts.append("Open")
        if dept_filter:
            filename_parts.append(dept_filter.replace(" ", "_"))
        if employee_filter:
            filename_parts.append(employee_filter.replace(" ", "_"))
        
        fname = f"{'_'.join(filename_parts)}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        
        logger.info(f"Exported {len(filtered)} tasks")
        return send_file(
            io.BytesIO(excel_bytes),
            download_name=fname,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Error in download_filtered: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/department/<dept_name>", methods=["GET"])
def get_department_tasks(dept_name: str):
    """Get tasks and statistics for a specific department."""
    try:
        df = repository.load_dataframe()
        dept_tasks = repository.search_tasks(df=df, vendor_filter=dept_name)
        
        open_tasks = repository.search_tasks(df=dept_tasks, status_filter="open")
        closed_tasks = repository.search_tasks(df=dept_tasks, status_filter="closed")
        
        employee_breakdown = open_tasks.groupby("Assigned to").size().reset_index(name="count")
        employee_breakdown = employee_breakdown.sort_values("count", ascending=False)
        
        logger.info(f"Retrieved department stats for {dept_name}")
        return jsonify({
            "department": dept_name,
            "total_tasks": len(dept_tasks),
            "open_tasks": len(open_tasks),
            "closed_tasks": len(closed_tasks),
            "tasks": dept_tasks.to_dict(orient="records"),
            "employee_breakdown": employee_breakdown.to_dict(orient="records")
        })
    except Exception as e:
        logger.error(f"Error in get_department_tasks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/employee/<employee_name>", methods=["GET"])
def get_employee_tasks(employee_name: str):
    """Get tasks and statistics for a specific employee."""
    try:
        df = repository.load_dataframe()
        employee_tasks = repository.search_tasks(df=df, employee_filter=employee_name)
        
        open_tasks = repository.search_tasks(df=employee_tasks, status_filter="open")
        closed_tasks = repository.search_tasks(df=employee_tasks, status_filter="closed")
        
        logger.info(f"Retrieved employee stats for {employee_name}")
        return jsonify({
            "employee": employee_name,
            "total_tasks": len(employee_tasks),
            "open_tasks": len(open_tasks),
            "closed_tasks": len(closed_tasks),
            "tasks": employee_tasks.to_dict(orient="records")
        })
    except Exception as e:
        logger.error(f"Error in get_employee_tasks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get overall statistics (cached for performance)."""
    try:
        stats = repository.get_statistics()
        logger.debug("Retrieved statistics")
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in get_stats: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5055))
    app.run(debug=False, port=port, host="0.0.0.0")
