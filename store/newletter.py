# # send_newsletters.py
# from django.core.management.base import BaseCommand
# from django.core.mail import send_mail
# from .models import Newsletter
# from django.conf import settings

# class Command(BaseCommand):
#     help = 'Send newsletters to all subscribers'

#     def handle(self, *args, **kwargs):
#         subscribers = Newsletter.objects.all()
#         email_list = [subscriber.email for subscriber in subscribers]

#         if not email_list:
#             self.stdout.write(self.style.WARNING('No subscribers found!'))
#             return

#         # Compose your email
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
#         self.stdout.write(self.style.SUCCESS('Successfully sent newsletter emails!'))
