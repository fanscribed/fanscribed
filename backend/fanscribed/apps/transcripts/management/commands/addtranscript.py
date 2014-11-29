from django.core.management.base import BaseCommand, CommandError

from unipath import Path


class Command(BaseCommand):

    args = '<url>'

    def handle(self, *args, **options):

        from ....media.models import MediaFile
        from ...models import Transcript

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
            self.stdout.write('Created media file: {}'.format(media_file))

        transcript = Transcript.objects.create(
            name=url,
        )
        if options['verbosity']:
            self.stdout.write('Created transcript: {}'.format(transcript))
