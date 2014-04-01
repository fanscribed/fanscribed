import random
from urlparse import urljoin

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
import requests

from ...apps.transcripts.models import TASK_MODEL


with open('/usr/share/dict/words', 'rb') as f:
    WORDS = f.read().split()


class Command(BaseCommand):
    args = '<base-url> <transcript-id> <email> <password>'
    help = "Benchmarks and stress-tests Fanscribed"

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity', 0)
        if len(args) != 4:
            raise CommandError(
                'Provide base URL, transcript ID, email, and password')
        self.base_url, self.transcript_id, self.email, self.password = args
        detail_path = reverse('transcripts:detail',
                              kwargs=dict(pk=self.transcript_id))
        self.transcript_url = urljoin(self.base_url, detail_path)
        self.session = requests.Session()
        self.login()
        while True:
            response = self.perform_any_task()
            if not response.ok:
                self.verbose_write('')
                self.verbose_write('  Response not OK:')
                self.verbose_write(response.content)
                break
            else:
                self.verbose_write('  Response OK.')
                #break

    def verbose_write(self, str):
        if self.verbosity > 0:
            self.stdout.write(str)

    def login(self):
        login_url = urljoin(self.base_url, '/accounts/login/')
        response = self.session.get(login_url)
        soup = BeautifulSoup(response.content)
        csrf_input = soup.find('input', dict(name='csrfmiddlewaretoken'))
        csrf_token = csrf_input.attrs['value']
        data = dict(
            csrfmiddlewaretoken=csrf_token,
            login=self.email,
            password=self.password,
        )
        response = self.session.post(login_url, data)
        assert response.ok, 'response not ok'
        assert response.url == self.base_url, 'did not redirect to base url'
        self.verbose_write('logged in')

    def perform_any_task(self):
        self.verbose_write('')

        response = self.session.get(self.transcript_url)
        soup = BeautifulSoup(response.content)
        csrf_input = soup.find('input', dict(name='csrfmiddlewaretoken'))
        csrf_token = csrf_input.attrs['value']

        # task_type = random.choice(['any_sequential', 'any_eager'])
        # task_type = 'transcribe'
        task_type = 'any_sequential'

        self.verbose_write('Requesting type: {task_type}'.format(**locals()))
        assign_path = reverse(
            'transcripts:task_assign', kwargs=dict(pk=self.transcript_id))
        assign_url = urljoin(self.transcript_url, assign_path)
        data = dict(
            type=task_type,
            csrfmiddlewaretoken=csrf_token,
        )
        response = self.session.post(assign_url, data, allow_redirects=True)
        task_url = response.url
        self.verbose_write('  assigned: {}'.format(task_url))
        if not response.ok:
            return response

        task_subpath = task_url.split(self.transcript_url)[1]
        assigned_task_type, assigned_task_id = task_subpath.split('/')[1:3]

        # Get whether or not it's a review by fetching the model.
        task_model = TASK_MODEL[assigned_task_type]
        task = task_model.objects.get(id=assigned_task_id)
        is_review = task.is_review

        self.verbose_write(
            '  type: {assigned_task_type}, is_review: {is_review}'.format(**locals()))

        perform_method_name = 'perform_{assigned_task_type}'.format(**locals())
        perform = getattr(self, perform_method_name)
        soup = BeautifulSoup(response.content)
        csrf_input = soup.find('input', dict(name='csrfmiddlewaretoken'))
        csrf_token = csrf_input.attrs['value']

        self.verbose_write('  performing:')
        return perform(task_url, soup, csrf_token, is_review)

    def perform_transcribe(self, url, soup, csrf_token, is_review):
        if not is_review:
            # Make 1-4 random sentences with 2-6 words each.
            sentences = []
            for i in range(1, random.randint(2, 5)):
                sentence = []
                for ii in range(1, random.randint(3, 7)):
                    sentence.append(random.choice(WORDS))
                sentence_text = ' '.join(sentence)
                sentences.append(sentence_text)
                self.verbose_write('    ' + sentence_text)
            text = '\n'.join(sentences)
        else:
            textarea = soup.find('textarea', dict(name='text'))
            text = textarea.contents
            alter = random.choice([True, False])
            if alter:
                # Add another word to beginning.
                text = '{} {}'.format(random.choice(WORDS), text)

        data = dict(
            text=text,
            csrfmiddlewaretoken=csrf_token,
        )
        return self.session.post(url, data)

    def perform_stitch(self, url, soup, csrf_token, is_review):
        if not is_review:
            pass
        else:
            pass

    def perform_clean(self, url, soup, csrf_token, is_review):
        if not is_review:
            pass
        else:
            pass

    def perform_boundary(self, url, soup, csrf_token, is_review):
        if not is_review:
            pass
        else:
            pass

    def perform_speaker(self, url, soup, csrf_token, is_review):
        if not is_review:
            pass
        else:
            pass
