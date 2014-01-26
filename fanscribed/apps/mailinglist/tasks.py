from django.conf import settings

from celery import shared_task

import mailchimp


@shared_task
def add_user_email_to_mailchimp(email, user_id):
    if settings.DEBUG:
        print 'Would have added {} to mailchimp.'.format(email)
    else:
        mc = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)
        mc.lists.batch_subscribe(
            id=settings.MAILCHIMP_LIST_ID,
            batch=[
                {
                    'email': {'email': email},
                    'email_type': 'html',
                    'merge_vars': {'USERID': user_id},
                },
            ],
            update_existing=True,
            relace_interests=False,
        )
