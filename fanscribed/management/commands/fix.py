from django.contrib.auth.models import User, Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.models import SocialAccount, SocialToken

from ...apps.media.models import MediaFile
from ...apps.transcripts.models import Transcript


class Command(BaseCommand):
    args = '<fixture_name>'
    help = "Builds a test data set"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError('Wrong arguments.')

        self.truncate_relevant_tables()

        call_command('load_initial_data',
                     verbosity=options['verbosity'], interactive=False)

        if options['verbosity'] > 0:
            self.stdout.write('Creating superuser "su".')
        superuser = User.objects.create_superuser(
            'su', 'superuser@example.com', 'su',
            first_name='Super', last_name='User')

        if options['verbosity'] > 0:
            self.stdout.write('Built test fixture.')

    def truncate_relevant_tables(self):
        self.truncate_tables([
            # admin
            'django_admin_log',
            # auth
            User,
            Group,
            'auth_group_permissions',
            'auth_user_groups',
            'auth_user_user_permissions',
            # allauth
            EmailAddress,
            EmailConfirmation,
            SocialAccount,
            SocialToken,
            'account_emailaddress',
            'account_emailconfirmation',
            # waffle
            'waffle_flag_groups',
            'waffle_flag_users',
            # media,
            MediaFile,
            # transcripts,
            Transcript,
        ])

    def truncate_tables(self, models_to_truncate):
        # http://stackoverflow.com/questions/2988997/
        cursor = connection.cursor()
        tables = [self.table_name(model) for model in models_to_truncate]
        tables_in_quotes = ['"{0}"'.format(table) for table in tables]
        sql = 'TRUNCATE TABLE {0} CASCADE'.format(','.join(tables_in_quotes))
        cursor.execute(sql)

    def table_name(self, model):
        return model if isinstance(model, basestring) else model._meta.db_table
