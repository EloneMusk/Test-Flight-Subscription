from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import threading
import time
import smtplib
import os
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from database import init_db, add_subscription, get_subscriptions, remove_subscriptions, add_status_history

app = Flask(__name__)
CORS(app)

# Initialize the database
init_db()

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')

def check_testflight_status(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if beta is full
        beta_full = bool(soup.find(string=re.compile("This beta is full", re.IGNORECASE)))
        
        # Get app icon URL
        icon_element = soup.find('img', class_='app-icon')
        icon_url = icon_element['src'] if icon_element else None
        
        return {
            'is_accepting': not beta_full,
            'icon_url': icon_url
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-status', methods=['POST'])
def check_status():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    if not url.startswith('https://testflight.apple.com/join/'):
        return jsonify({'error': 'Invalid TestFlight URL'}), 400
    
    result = check_testflight_status(url)
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
        
    return jsonify(result)

def send_notification_email(recipient_email, url):
    try:
        message = MIMEMultipart()
        message['From'] = EMAIL_USER
        message['To'] = recipient_email
        message['Subject'] = 'TestFlight Beta is Now Open!'

        body = f"Good news! The TestFlight beta you subscribed to is now accepting new testers.\n\nYou can join the beta here: {url}"
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f'Failed to send email: {str(e)}')
        return False

def check_and_notify():
    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_time}] Checking TestFlight status for subscriptions...')
        
        urls = get_subscriptions()
        for url in urls:
            try:
                result = check_testflight_status(url)
                add_status_history(url, result.get('is_accepting', False))
                
                if result.get('is_accepting'):
                    emails = get_subscriptions(url)
                    for email in emails:
                        if send_notification_email(email, url):
                            print(f'Notification sent to {email} for {url}')
                    # Remove subscriptions after notification
                    remove_subscriptions(url)
            except Exception as e:
                print(f'Error checking status for {url}: {str(e)}')
        time.sleep(300)  # Check every 5 minutes

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    url = data.get('url')
    
    if not email or not url:
        return jsonify({'error': 'Email and URL are required'}), 400
    
    if not url.startswith('https://testflight.apple.com/join/'):
        return jsonify({'error': 'Invalid TestFlight URL'}), 400

    if add_subscription(email, url):
        return jsonify({'message': 'Successfully subscribed'})
    
    return jsonify({'message': 'Already subscribed'})

@app.route('/subscriptions', methods=['GET'])
def get_user_subscriptions():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    try:
        # Get all subscriptions for the email
        with sqlite3.connect('testflight.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT url, datetime(created_at, \'localtime\') as created_at FROM subscriptions WHERE email = ?',
                (email,)
            )
            subscriptions = [{'url': row[0], 'created_at': row[1]} for row in cursor.fetchall()]
            return jsonify({'subscriptions': subscriptions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.get_json()
    email = data.get('email')
    url = data.get('url')

    if not email or not url:
        return jsonify({'error': 'Email and URL are required'}), 400

    try:
        with sqlite3.connect('testflight.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM subscriptions WHERE email = ? AND url = ?',
                (email, url)
            )
            conn.commit()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start the background checker in a separate thread
    checker_thread = threading.Thread(target=check_and_notify, daemon=True)
    checker_thread.start()
    
    app.run(host='0.0.0.0', port=8000, debug=True)