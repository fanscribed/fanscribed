# TODO: port this tool to use an API when it's available
from decimal import Decimal

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

        task_type = random.choice(['any_sequential', 'any_eager'])

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
        data = dict(
            csrfmiddlewaretoken=csrf_token,
        )

        self.verbose_write('  performing:')
        return perform(task_url, soup, data, is_review)

    def perform_transcribe(self, url, soup, data, is_review):
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
            text = ''.join(textarea.contents)
            alter = random.choice([True, False])
            if alter:
                # Add another word to beginning.
                text = '{} {}'.format(random.choice(WORDS), text)
                self.verbose_write('    (changed text)')

        data['text'] = text
        return self.session.post(url, data)

    def perform_stitch(self, url, soup, data, is_review):
        # Find the set of left-side and right-side candidates.
        left = set()
        right = set()
        for tag in soup.find_all('input', dict(type='radio')):
            name = tag.attrs['name']
            left.add(name)
            value = tag.attrs['value']
            if value != '-':
                right.add(value)
            if tag.attrs.get('checked') == 'checked':
                data[name] = value
        self.verbose_write(repr(left))
        self.verbose_write(repr(right))

        if not is_review:
            # Join a random number of fragments on the right to the left.
            max_stitch_count = min(len(left), len(right))
            stitch_count = random.randint(0, max_stitch_count)
            for i in range(0, stitch_count):
                value = random.choice(list(right))
                right.remove(value)
                name = random.choice(list(left))
                left.remove(name)
                data[name] = value
                self.verbose_write('    {} <- {}'.format(name, value))
        else:
            alter = random.choice([True, False])
            if alter:
                name = random.choice(list(left))
                data[name] = '-'

        return self.session.post(url, data)

    def perform_clean(self, url, soup, data, is_review):
        # Do the same thing whether or not we are reviewing.
        textarea = soup.find('textarea', dict(name='text'))
        text = ''.join(textarea.contents)
        alter = random.choice([True, False])

        if alter:
            # Add another word to beginning.
            text = '{} {}'.format(random.choice(WORDS), text)
            self.verbose_write('    (changed text)')

        data['text'] = text
        return self.session.post(url, data)

    def perform_boundary(self, url, soup, data, is_review):
        start_tag = soup.find('input', dict(name='start'))
        end_tag = soup.find('input', dict(name='end'))
        start = Decimal(start_tag.attrs['value'])
        end = Decimal(end_tag.attrs['value'])

        if not is_review:
            max_delta = (end - start) / 2
            delta1 = Decimal(random.randint(0, int(max_delta * 100))) / 100
            delta2 = Decimal(random.randint(0, int(max_delta * 100))) / 100
            delta_start, delta_end = sorted([delta1, delta2])
            self.verbose_write('    {}, {}'.format(delta_start, delta_end))
            start += delta_start
            end -= delta_end
            self.verbose_write('    {} -> {}'.format(start, end))
        else:
            alter = random.choice([True, False])
            if alter:
                start -= Decimal('0.01')
                end += Decimal('0.01')

        data['start'] = str(start)
        data['end'] = str(end)
        return self.session.post(url, data)

    def perform_speaker(self, url, soup, data, is_review):
        speakers = []
        speaker_inputs = soup.find_all('input', dict(type='radio'))
        for tag in speaker_inputs:
            value = tag.attrs.get('value')
            if value:
                speakers.append(value)
                if tag.attrs.get('checked') == 'checked':
                    data['speaker'] = value

        if not is_review:
            if len(speakers) == 0:
                create_new = True
            else:
                create_new = (random.random() < 0.1)
            if create_new:
                new_name = random.choice(WORDS)
                data['new_name'] = new_name
                if 'speaker' in data:
                    del data['speaker']
                self.verbose_write('    new speaker: {}'.format(new_name))
            else:
                speaker = random.choice(speakers)
                data['speaker'] = speaker
                self.verbose_write('   existing speaker: {}'.format(speaker))
        else:
            alter = random.choice([True, False])
            if alter:
                data['speaker'] = random.choice(speakers)

        return self.session.post(url, data)
