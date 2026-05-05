# Task Ticket Tracker - Deployment Guide

## Overview
This is a Flask-based Task Ticket Tracker application that manages tickets with dashboard visualization, Excel export, and more.

## Deployment to Render

### Prerequisites
- GitHub account
- Render account (free tier available at render.com)
- The code pushed to GitHub (already done!)

### Step-by-Step Deployment Instructions

#### **Step 1: Sign Up for Render**
1. Go to [render.com](https://render.com)
2. Click "Get Started" and sign up with your GitHub account
3. Authorize Render to access your GitHub repositories

#### **Step 2: Create a Web Service on Render**
1. In your Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Choose your GitHub repository: `Task_Ticket_Tracker`
4. Connect your repository (if prompted)

#### **Step 3: Configure the Service**
Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | task-ticket-tracker (or your preferred name) |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | Free (or paid if needed) |

#### **Step 4: Environment Variables (Optional)**
If you need custom environment variables, add them in the "Environment" tab:
- Leave blank for now (defaults will work)

#### **Step 5: Deploy**
1. Click **"Create Web Service"**
2. Render will automatically:
   - Build your application
   - Install all dependencies from `requirements.txt`
   - Start your service with `gunicorn`
   - Assign you a unique URL (e.g., `task-ticket-tracker.onrender.com`)

3. Wait for deployment to complete (usually 2-5 minutes)
4. Once "Live" status appears, your app is running!

#### **Step 6: Access Your App**
- Your app will be available at: `https://<your-service-name>.onrender.com`
- Share this URL with anyone who needs access
- It runs 24/7 independently (even when your laptop is off)

---

## What's Included in This Deployment

✅ **Procfile** - Tells Render how to run the app  
✅ **requirements.txt** - All Python dependencies  
✅ **runtime.txt** - Python version specification  
✅ **.gitignore** - Excludes unnecessary files  
✅ **app.py** - Updated to use environment PORT variable  
✅ **dashboard.html** - Your frontend interface  
✅ **HO_Ticket_Tracker.xlsx** - Data file (stored on Render)

---

## Important Notes

### Data Persistence
- Your Excel file (`HO_Ticket_Tracker.xlsx`) is stored on the Render instance
- Data persists between app restarts
- **Warning**: Render's free tier instances get spun down after 15 minutes of inactivity, but data is retained

### Upgrading from Free to Paid
If you need always-on service:
1. Go to your Render dashboard
2. Click on your service
3. Go to "Settings" → "Instance Type"
4. Upgrade to "Standard" or higher

### Automatic Deployments
- Every time you push to the `master` branch on GitHub, Render automatically deploys
- No manual deployment needed!

### Monitoring Your Service
1. In Render dashboard, click your service name
2. View real-time logs
3. Check service status and metrics
4. Monitor CPU and memory usage

---

## Troubleshooting

### App Won't Deploy
- Check build logs in Render dashboard
- Ensure `Procfile` exists in root directory
- Verify `requirements.txt` contains all dependencies

### Port Issues
- App automatically uses PORT environment variable
- No configuration needed

### Performance Slow
- Free tier instances may be slower
- Consider upgrading to paid instance for better performance

### Need to Update Code
1. Make changes locally
2. Commit: `git add .` → `git commit -m "description"`
3. Push: `git push origin master`
4. Render automatically redeploys

---

## Support
- Render Docs: https://render.com/docs
- Flask Docs: https://flask.palletsprojects.com/
- GitHub Issues: Post in your GitHub repo

---

**Your app is now live on the cloud! 🚀**
