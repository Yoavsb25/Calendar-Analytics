
# Google Calendar Event Analyzer

A Flask web application that allows users to analyze their Google Calendar events by month using OAuth 2.0 authentication. The app generates a summary of the people you met during a selected month based on calendar events and provides a seamless experience with secure authentication.

---

## 🚀 Features

- **Google OAuth Login**: Secure login using your Google account.
- **Monthly Event Summary**: Analyze events by selecting a month and viewing a list of people you met during that time.
- **Secure Credential Management**: OAuth tokens and credentials are securely stored and managed.
- **User-Friendly Interface**: Simple and intuitive web interface to interact with your Google Calendar data.

---

## 🛠️ Prerequisites

Before running the application, ensure you have the following:

- Python 3.8+
- Google Cloud Project
- Google Calendar API enabled

---

## 💻 Installation

Follow these steps to get your development environment set up:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/google-calendar-event-analyzer.git
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:

    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```

4. **Install the required dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

5. **Configure Google OAuth credentials**: Follow the steps in the [Google Cloud Console](https://console.cloud.google.com/), create OAuth credentials, and download the JSON file.

6. **Set up the `.env` file**: Create a `.env` file at the root of your project and add the following:

    ```plaintext
    GOOGLE_CLIENT_ID=your-client-id
    GOOGLE_CLIENT_SECRET=your-client-secret
    GOOGLE_OAUTH_REDIRECT_URI=your-redirect-uri
    ```

---

## ⚙️ Configuration

1. **Obtain Google OAuth credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and enable the **Google Calendar API**.
   - Generate OAuth credentials and download the `client_secret.json` file.
   
2. **Configure OAuth Scopes**:
   - Set up the OAuth scope to allow access to the **Google Calendar API** and **Google userinfo**:

    ```python
    scope=["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/userinfo.email"]
    ```

3. **Set up `.env` file**:
   - Add your OAuth client ID and client secret to the `.env` file (see the installation section for details).

---

## 🔐 Security

- The application securely manages OAuth tokens, using environment variables to prevent credential exposure.
- OAuth tokens are refreshed when necessary to ensure uninterrupted access to the Google Calendar API.
- **No credentials are stored in version control** – they are always retrieved from the environment or Google Cloud.

---

## 🛠️ Technologies Used

- **Flask**: Lightweight web framework for building the app.
- **Google OAuth**: For secure user authentication and authorization.
- **Google Calendar API**: To retrieve and analyze calendar events.
- **Environment Variables**: To securely manage sensitive information.

---

## 📝 Setup Steps

1. **Create a Google Cloud Project**:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/), create a new project, and enable the **Google Calendar API**.

2. **Generate OAuth Client Credentials**:
   - In the Google Cloud Console, create OAuth credentials and download the `client_secret.json` file.

3. **Configure `.env` File**:
   - Set up the `.env` file with your client ID and client secret as described above.

4. **Run the Application**:
   - Start the Flask development server:
     ```bash
     python app.py
     ```
   - Visit `http://127.0.0.1:5000` in your browser to start using the app.

---

## 🏁 Usage

1. **Login**: Sign in with your Google account via the OAuth flow.
2. **Select a Month**: Choose a month to analyze your calendar events.
3. **View Event Summary**: See the list of people you met during the selected month based on the attendees of your Google Calendar events.

---

## 🙌 Contributing

Contributions are welcome! Feel free to fork the repository, create a branch, and submit a pull request. Please make sure to follow the guidelines provided.

