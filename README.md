# TestFlight Status Checker 🚀

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A web application that monitors TestFlight beta slots and notifies users when spaces become available. Never miss a beta testing opportunity again!

## Features ✨

- 🔍 Real-time monitoring of TestFlight beta availability
- 📧 Email notifications when beta slots open up
- 🌐 Web interface for managing subscriptions
- 📊 Status history tracking
- 🔄 Automatic cleanup of fulfilled notifications

## Setup 🛠️

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd TestFlight
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure email settings:
   - Set environment variables:
     ```bash
     export EMAIL_USER="your-email@gmail.com"
     export EMAIL_PASSWORD="your-app-password"
     ```
   Note: For Gmail, you'll need to use an App Password. [Learn how to create one](https://support.google.com/accounts/answer/185833?hl=en)

### Running the Application

1. Initialize the database:
   ```bash
   python database.py
   ```

2. Start the server:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:8000`

## Usage 💡

### Subscribe to Beta Notifications

1. Visit the web interface at `http://localhost:8000`
2. Enter your email address and the TestFlight beta URL
3. Click "Subscribe"

### View Your Subscriptions

- Use the `/subscriptions` endpoint with your email as a query parameter:
  ```
  GET http://localhost:8000/subscriptions?email=your-email@example.com
  ```

### Unsubscribe

- Send a POST request to `/unsubscribe` with your email and the TestFlight URL:
  ```json
  POST http://localhost:8000/unsubscribe
  {
    "email": "your-email@example.com",
    "url": "https://testflight.apple.com/join/..."
  }
  ```

## How It Works 🔄

1. The application periodically checks TestFlight beta URLs every 5 minutes
2. When a beta slot becomes available:
   - Subscribed users receive an email notification
   - Their subscription is automatically removed
3. Status history is maintained in the database for tracking purposes

## Database Schema 📚

### Subscriptions Table
- `id`: Primary key
- `email`: User's email address
- `url`: TestFlight beta URL
- `created_at`: Subscription timestamp

### Status History Table
- `id`: Primary key
- `url`: TestFlight beta URL
- `is_accepting`: Beta availability status
- `checked_at`: Status check timestamp

## API Endpoints 🔌

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/check-status` | POST | Check current beta availability |
| `/subscribe` | POST | Subscribe to notifications |
| `/unsubscribe` | POST | Remove a subscription |
| `/subscriptions` | GET | List user's subscriptions |

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💪

If you encounter any issues or have questions, please open an issue on the repository.