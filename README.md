# Calendar Analytics

![Python](https://img.shields.io/badge/Python-A78BFA?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-7C3AED?style=for-the-badge&logo=flask&logoColor=white)
![Google Calendar](https://img.shields.io/badge/Google_Calendar_API-A78BFA?style=for-the-badge&logo=googlecalendar&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-7C3AED?style=for-the-badge)

> Flask app that connects to Google Calendar, aggregates events by name, and exports revenue reports as CSV.

---

## Overview

Calendar Analytics authenticates with Google OAuth 2.0, fetches events from your primary Google Calendar for a selected date range, and aggregates them by event name. You can assign a price per meeting type and export the final report as a CSV — useful for freelancers and consultants tracking billable sessions.

## Features

- Google OAuth 2.0 login via Flask-Dance
- Select any custom date range for analysis
- Event aggregation by name with occurrence count
- Editable price-per-meeting for each event type
- One-click CSV export with per-event totals and grand total row
- Deployed on Heroku via Procfile

## OAuth Flow

```
User → GET /
     → Redirect to Google OAuth
     → Google → GET /login/authorized (callback)
     → Store token in session
     → Redirect to /select-month
     → POST /generate-report → Fetch Google Calendar API → Render editable report
     → POST /save-report → Calculate totals → Download CSV
```

## Routes

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Login page |
| GET | `/login/authorized` | Google OAuth callback — validates token, redirects to date selector |
| GET | `/select-month` | Date range selection form (requires auth) |
| POST | `/generate-report` | Fetches events from Google Calendar API, counts by name, renders editable report |
| POST | `/save-report` | Collects pricing from form, calculates totals, returns CSV download |

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-flask-secret-key
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_OAUTH_SCOPES=https://www.googleapis.com/auth/calendar.readonly,https://www.googleapis.com/auth/userinfo.email
```

> Get credentials from [Google Cloud Console](https://console.cloud.google.com/) — create an OAuth 2.0 Client ID with redirect URI `http://localhost:5000/login/authorized`.

## Getting Started

**Prerequisites:** Python 3.x, pip

```bash
git clone https://github.com/Yoavsb25/Calendar-Analytics.git
cd Calendar-Analytics
pip install -r requirements.txt
# Create .env with your credentials (see above)
python app.py
```

Open http://localhost:5000

## Project Structure

```
Calendar-Analytics/
├── app.py              # Flask app — all routes, OAuth setup, Calendar API calls
├── config.py           # Config class (SECRET_KEY, Google OAuth settings)
├── requirements.txt    # Python dependencies
├── Procfile            # Heroku deployment config
├── runtime.txt         # Python version pin for Heroku
├── static/             # CSS and JS assets
└── templates/
    ├── login.html          # OAuth login page
    ├── select_month.html   # Date range selection form
    └── report.html         # Editable event report with pricing fields
```

---

[![LinkedIn](https://img.shields.io/badge/Yoav_Sborovsky-LinkedIn-7C3AED?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yoav-sborovsky/)
&nbsp;
Part of [Yoav Sborovsky's GitHub portfolio](https://github.com/Yoavsb25)
