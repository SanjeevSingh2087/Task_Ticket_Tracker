#!/bin/bash
echo "================================================"
echo "  HO Ticket Tracker - Starting Backend Server"
echo "================================================"
echo ""

# Check dependencies
pip install flask flask-cors openpyxl pandas -q 2>/dev/null

echo "Starting Flask API on http://localhost:5055"
echo "Open dashboard.html in your browser after this starts."
echo ""
python app.py
