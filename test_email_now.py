#!/usr/bin/env python3
"""Test email sending right now"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_TO = 'masterai6612@gmail.com'
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

print(f'Testing email configuration...')
print(f'From: {EMAIL_FROM}')
print(f'To: {EMAIL_TO}')
print(f'Password: {"*" * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else "NOT SET"}')

try:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = '🧪 Test Email - Stock Alert System'
    
    body = '''
This is a test email from your Stock Alert System.

If you receive this, your email configuration is working correctly!

✅ System is operational
📧 Email alerts are enabled
🚀 Ready to send stock recommendations

Test sent at: ''' + str(os.popen('date').read())
    
    msg.attach(MIMEText(body, 'plain'))
    
    print('Connecting to Gmail SMTP...')
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        print('Logging in...')
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        print('Sending email...')
        server.send_message(msg)
    
    print('✅ Test email sent successfully!')
    print(f'📧 Check your inbox at {EMAIL_TO}')
    print('📧 Also check your SPAM folder if you don\'t see it')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
