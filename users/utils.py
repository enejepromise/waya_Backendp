# utils.py
import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings

def send_email(subject, message, to_email):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    email = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=message,
    )
    response = sg.send(email)
    return response
