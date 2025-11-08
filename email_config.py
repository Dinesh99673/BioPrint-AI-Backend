"""
Email Configuration for BioPrint API

Replace the dummy values with your actual email credentials.
For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password instead of your regular password
"""

# Email Configuration
# Replace these with your actual email credentials
EMAIL_CONFIG = {
    "SMTP_SERVER": "smtp.gmail.com",  # Gmail SMTP server
    "SMTP_PORT": 587,                 # Gmail SMTP port
    "SMTP_USERNAME": "your_email@gmail.com",  # Your Gmail address
    "SMTP_PASSWORD": "your_app_password",     # Your Gmail App Password
}

# Alternative configurations for other email providers:

# For Outlook/Hotmail:
# EMAIL_CONFIG = {
#     "SMTP_SERVER": "smtp-mail.outlook.com",
#     "SMTP_PORT": 587,
#     "SMTP_USERNAME": "your_email@outlook.com",
#     "SMTP_PASSWORD": "your_password",
# }

# For Yahoo:
# EMAIL_CONFIG = {
#     "SMTP_SERVER": "smtp.mail.yahoo.com",
#     "SMTP_PORT": 587,
#     "SMTP_USERNAME": "your_email@yahoo.com",
#     "SMTP_PASSWORD": "your_app_password",
# }

# For custom SMTP server:
# EMAIL_CONFIG = {
#     "SMTP_SERVER": "your_smtp_server.com",
#     "SMTP_PORT": 587,  # or 465 for SSL
#     "SMTP_USERNAME": "your_username",
#     "SMTP_PASSWORD": "your_password",
# }

# Instructions for Gmail App Password:
"""
1. Go to your Google Account settings
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click "2-Step Verification"
4. At the bottom of the page, click "App passwords"
5. Select "Mail" and "Other (Custom name)" from the dropdown
6. Enter "BioPrint API" as the name
7. Click "Generate"
8. Copy the 16-character password and use it as SMTP_PASSWORD
"""

# Instructions for testing:
"""
1. Update the EMAIL_CONFIG with your actual credentials
2. Import this config in your app.py:
   from email_config import EMAIL_CONFIG
3. Update the SMTP variables in app.py:
   SMTP_SERVER = EMAIL_CONFIG["SMTP_SERVER"]
   SMTP_PORT = EMAIL_CONFIG["SMTP_PORT"]
   SMTP_USERNAME = EMAIL_CONFIG["SMTP_USERNAME"]
   SMTP_PASSWORD = EMAIL_CONFIG["SMTP_PASSWORD"]
4. Test the email functionality using the test script
"""
