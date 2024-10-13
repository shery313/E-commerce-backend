# # tasks.py
# from celery import shared_task
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import Newsletter

# @shared_task
# def send_newsletter_emails():
#     subscribers = Newsletter.objects.all()
#     email_list = [subscriber.email for subscriber in subscribers]

#     if email_list:
#         subject = 'Your Monthly Newsletter'
#         message = 'Hello, here is the latest news from our store!'
#         from_email = settings.EMAIL_HOST_USER

#         # Send the email to all subscribers
#         send_mail(
#             subject,
#             message,
#             from_email,
#             email_list,
#             fail_silently=False,
#         )
#         return f'Successfully sent newsletter to {len(email_list)} subscribers.'
#     else:
#         return 'No subscribers found.'
