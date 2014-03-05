from django.core.management.base import BaseCommand, CommandError

from unipath import Path


class Command(BaseCommand):

    args = '<url>'

    def handle(self, *args, **options):

        from ...models import MediaFile

        if len(args) != 1:
            raise CommandError('Provide media URL.')

        (url,) = args

        local_path = Path(url)
        if local_path.exists():
            url = 'file://{}'.format(local_path.absolute())

        media_file = MediaFile.objects.create(
            data_url=url,
        )
        if options['verbosity']:
            self.stdout.write('Created: {}'.format(media_file))
