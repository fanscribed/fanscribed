from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load initial data"

    def handle(self, *args, **options):
        if options['verbosity'] > 0:
            self.stdout.write('Loaded initial data.')
