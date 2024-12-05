from flask import Flask, redirect, url_for, session, render_template, request, flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.session import SessionStorage
from flask_dance.contrib.google import make_google_blueprint, google
from googleapiclient.discovery import build
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)

# App setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Google OAuth setup
google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    scope=os.getenv('GOOGLE_OAUTH_SCOPES', '').split(','),
    storage=SessionStorage(),
    redirect_to="authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Log the successful login and token exchange
@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        flash('Google login failed.', category='error')
        logging.error('Google login failed. No token received.')
        return False

    # Store token for further use
    session['google_token'] = token
    logging.info(f"Google login successful. Token: {token}")
    return True

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login/authorized")
def authorized():
    if not google.authorized:
        error_msg = 'Authorization failed. Details: google.authorized is False'
        logging.error(error_msg)
        flash(error_msg, category='error')
        return redirect(url_for("google.login"))

    try:
        # Get user info after successful OAuth authorization
        resp = google.get("/oauth2/v2/userinfo")

        # Log full response details for debugging
        logging.error(f"Full response status: {resp.status_code}")
        logging.error(f"Full response headers: {resp.headers}")
        logging.error(f"Full response text: {resp.text}")

        if not resp.ok:
            error_msg = f'Authentication failed. Status: {resp.status_code}, Text: {resp.text}'
            logging.error(error_msg)
            flash(error_msg, category='error')
            return redirect(url_for("index"))

        logging.info(f"User info retrieved: {resp.json()}")
        return redirect(url_for("select_month"))

    except Exception as e:
        logging.error(f"Detailed authorization error: {e}", exc_info=True)
        flash(f'Authorization error: {str(e)}', category='error')
        return redirect(url_for("index"))
@app.route("/select-month")
def select_month():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("select_month.html")


@app.route("/generate-report", methods=["POST"])
def generate_report():
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        # Get the OAuth token
        token = google.token

        # Create credentials from the token
        from google.oauth2.credentials import Credentials
        credentials = Credentials(
            token=token['access_token'],
            refresh_token=token.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id='657802434191-hkm4bqm4vdq2omm864v2mjcdbha4csqb.apps.googleusercontent.com',
            client_secret='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'
        )

        # Handle selected month
        selected_month = request.form["month"]
        current_year = datetime.now().year
        month = int(selected_month)

        # Set start date to the first of the month at midnight
        start_date = datetime(current_year, month, 1, 0, 0, 0).isoformat() + 'Z'

        # Set end date to the last day of the month at 23:59:59
        if month == 12:
            end_date = datetime(current_year + 1, 1, 1, 0, 0, 0).isoformat() + 'Z'
        else:
            end_date = datetime(current_year, month + 1, 1, 0, 0, 0).isoformat() + 'Z'

        # Make API call to Google Calendar
        service = build("calendar", "v3", credentials=credentials)
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        # Collect unique event names and their meeting counts
        event_counts = {}
        for event in events_result.get("items", []):
            event_name = event.get("summary", "Untitled Event")
            event_counts[event_name] = event_counts.get(event_name, 0) + 1

        logging.info(f"Unique events in {month}-{current_year}: {event_counts}")
        return render_template("report.html", events=event_counts, month=month, year=current_year)

    except Exception as e:
        logging.error(f"Error generating report: {e}", exc_info=True)
        flash('Report generation failed. Please try again.', category='error')
        return redirect(url_for("select_month"))

if __name__ == "__main__":
    app.run(debug=True)
