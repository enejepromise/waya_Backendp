from celery import shared_task
#from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


# @shared_task
# def send_email_task(subject, to_email, html_content):
#     message = Mail(
#         from_email=settings.SENDGRID_SENDER_EMAIL,
#         to_emails=to_email,
#         subject=subject,
#         html_content=html_content
#     )
#     try:
#         sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
#         response = sg.send(message)
#         return response.status_code
#     except Exception as e:
#         # Log error in production
#         print(f"SendGrid error: {e}")
#         return None
    
@shared_task
def send_verification_email_async(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )


@shared_task
def send_email_task(subject, recipient_email, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )
