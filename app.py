from flask import Flask, redirect, url_for, session, render_template, request, flash
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.session import SessionStorage
from flask_dance.contrib.google import make_google_blueprint, google
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import csv
from flask import send_file
import io
from dotenv import load_dotenv
import logging
from google.oauth2.credentials import Credentials

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
        # Get start and end dates from form
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d")

        # Add one day to end_date to include the entire last day
        end_date = end_date + timedelta(days=1)

        # Convert to ISO format for Google Calendar API
        start_date_iso = start_date.isoformat() + 'Z'
        end_date_iso = end_date.isoformat() + 'Z'

        # Make API call to Google Calendar
        response = google.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            params={
                "timeMin": start_date_iso,
                "timeMax": end_date_iso,
                "singleEvents": True,
                "orderBy": "startTime"
            }
        )

        if not response.ok:
            logging.error(f"Failed to fetch events: {response.text}")
            flash("Failed to retrieve calendar events.", category='error')
            return redirect(url_for("select_month"))

        # Process events from response
        events_result = response.json()
        event_counts = {}
        for event in events_result.get("items", []):
            event_name = event.get("summary", "Untitled Event")
            event_counts[event_name] = event_counts.get(event_name, 0) + 1

        # Create a list of events with count and default price
        event_details = [
            {
                'name': event_name,
                'count': count,
                'price': 0.0,
                'total': 0.0
            }
            for event_name, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        # Format dates for display
        formatted_start = start_date.strftime("%Y-%m-%d")
        formatted_end = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")

        logging.info(f"Generated report for period {formatted_start} to {formatted_end}")
        return render_template("report.html",
                               events=event_details,
                               start_date=formatted_start,
                               end_date=formatted_end,
                               editable=True)

    except Exception as e:
        logging.error(f"Error generating report: {e}", exc_info=True)
        flash('Report generation failed. Please try again.', category='error')
        return redirect(url_for("select_month"))


@app.route("/save-report", methods=["POST"])
def save_report():
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Capture form data
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Collect event details
    event_details = []
    for i in range(len(request.form)):
        try:
            price_key = f'price_{i}'
            if price_key in request.form:
                event_name = request.form.get(f'event_name_{i}', 'Unknown')
                count = int(request.form.get(f'count_{i}', 0))
                price = float(request.form.get(price_key, 0))
                total = count * price

                event_details.append({
                    'Event Name': event_name,
                    'Number of Meetings': count,
                    'Price per Meeting': f'${price:.2f}',
                    'Total Revenue': f'${total:.2f}'
                })
        except Exception as e:
            logging.error(f"Error processing event {i}: {e}")

    # Generate CSV in memory
    output = io.StringIO(newline="")
    fieldnames = ['Event Name', 'Number of Meetings', 'Price per Meeting', 'Total Revenue']
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')

    # Write headers and rows
    writer.writeheader()
    writer.writerows(event_details)

    # Calculate grand total
    grand_total = sum(float(item['Total Revenue'].replace('$', '')) for item in event_details)
    writer.writerow({
        'Event Name': 'Grand Total',
        'Total Revenue': f'${grand_total:.2f}'
    })

    # Prepare CSV for download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'event_report_{start_date}_{end_date}.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)
