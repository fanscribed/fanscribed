from django.dispatch import receiver

from allauth.account.signals import user_signed_up

from .tasks import add_user_email_to_mailchimp


@receiver(user_signed_up)
def add_to_mailchimp(sender, request, user, **kwargs):
    for email in user.emailaddress_set.filter(primary=True):
        add_user_email_to_mailchimp.delay(email.email, user.id)
