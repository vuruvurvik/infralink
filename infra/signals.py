# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to Our Site'
        message = f'Hi {instance.username}, thank you for registering at our site!'
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email

        send_mail(subject, message, from_email, [to_email])
# signals.py (for sending SMS)
import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from twilio.rest import Client
from .models import UserProfile

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def send_welcome_sms(sender, instance, created, **kwargs):
    if created:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Hello {instance.user.username}, welcome to our platform!',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=instance.phone  # Ensure the phone number is in the correct format
            )
            logger.info(f'SMS sent to {instance.phone}. Message SID: {message.sid}')
        except Exception as e:
            logger.error(f'Failed to send SMS: {e}')

# signals.py (same file as above)
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


