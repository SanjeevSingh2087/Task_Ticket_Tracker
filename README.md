# HO Ticket Tracker

A Flask-based Task Ticket Tracker with a browser dashboard, ticket management, Excel storage, and export capabilities.

## Features

- Create and update tickets via a dashboard UI
- Store ticket data in `HO_Ticket_Tracker.xlsx`
- Export filtered tasks to a styled Excel workbook
- View department and employee task summaries
- Verify delete actions with a code-based confirmation
- Runs with `gunicorn` for production deployments

## Project Structure

- `app.py` - Flask backend and Excel data management
- `dashboard.html` - Frontend dashboard UI
- `requirements.txt` - Python dependency list
- `Procfile` - Deployment entrypoint for Render/Heroku
- `runtime.txt` - Python runtime version
- `DEPLOYMENT_GUIDE.md` - Deploy instructions for Render
- `HO_Ticket_Tracker.xlsx` - Excel data file (created automatically when missing)

## Requirements

- Python 3.12
- Virtual environment recommended

## Installation

1. Clone the repository

```bash
git clone <your-repo-url>
cd files
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5055/
```

## Deployment

This project is configured for deployment with Render or similar Python hosting.

- `Procfile` uses:
  - `web: gunicorn app:app`
- `runtime.txt` specifies Python 3.12

For Render, the build command is:

```bash
pip install -r requirements.txt
```

And the start command is:

```bash
gunicorn app:app
```

## API Endpoints

- `GET /` - Serve the dashboard
- `GET /api/tasks` - Return all tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/<ticket_no>` - Update an existing task
- `DELETE /api/tasks/<ticket_no>` - Delete a task (requires delete code)
- `POST /api/verify-delete-code` - Verify delete code before deletion
- `GET /api/download` - Export filtered task list as Excel
- `GET /api/department/<dept_name>` - Get department task summary
- `GET /api/employee/<employee_name>` - Get employee task summary
- `GET /api/stats` - Get overall task statistics

## Notes

- `HO_Ticket_Tracker.xlsx` is auto-created if missing.
- Deletion requires the verification code: `1947`
- The app reads and writes directly to the Excel workbook, so keep the file accessible to the app.

## License

Use and modify this project freely.
