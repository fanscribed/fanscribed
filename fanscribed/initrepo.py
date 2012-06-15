import os
import shutil
import subprocess
import urllib

import git
import json

from paste.deploy.loadwsgi import loadapp
from paste.script.command import Command

from fanscribed import mp3


class InitRepoCommand(Command):

    min_args = 1
    usage = 'CONFIG_FILE'
    takes_config_file = 1
    summary = 'Initialize a new transcript repository'
    description = """\
    This command initializes a new transcript repository based on
    a template you select and variables you provide.
    """
    default_verbosity = 1

    parser = Command.standard_parser()

    def command(self):
        # Load config file.
        app_spec = 'config:{0}'.format(self.args[0])
        base = os.getcwd()
        app = loadapp(app_spec, name='main', relative_to=base, global_conf={})
        # Read settings.
        settings = app.registry.settings
        audio_path = settings['fanscribed.audio']
        repos_path = settings['fanscribed.repos']
        templates_path = settings['fanscribed.repo_templates']
        snippet_seconds = int(settings['fanscribed.snippet_seconds'])
        # Make sure paths exist.
        if not os.path.isdir(templates_path):
            print 'Repo templates path {0} does not exist'.format(templates_path)
            return 1
        template_names = os.listdir(templates_path)
        if not template_names:
            print 'No templates exist in repo templates path {0}'.format(templates_path)
            return 1
        # Ask for a unique site name.
        is_valid_host_name = False
        host_name = None
        repo_path = None
        while not is_valid_host_name:
            host_name = self.challenge('Host name of new transcript')
            repo_path = os.path.join(repos_path, host_name)
            is_valid_host_name = not os.path.exists(repo_path)
            if not is_valid_host_name:
                print '{0} already exists'.format(repo_path)
        # Ask for audio URL.
        audio_url = self.challenge('Audio URL')
        # Ask for the template.
        print 'Available templates: {0}'.format(', '.join(template_names))
        is_valid_template = False
        variables_txt_path = None
        template_path = None
        while not is_valid_template:
            template_name = self.challenge('Template for new transcript')
            template_path = os.path.join(templates_path, template_name)
            variables_txt_path = os.path.join(template_path, 'variables.txt')
            is_valid_template = os.path.isfile(variables_txt_path)
            if not is_valid_template:
                print '{0} is not a valid template'.format(template_name)
        # Ask for all the variables in the template.
        variables = {}
        with open(variables_txt_path, 'rU') as f:
            for line in f.readlines():
                line = line.strip()
                parts = line.split(';', 1)
                if len(parts) != 2:
                    # Not a valid variable definition.
                    continue
                name, description = (part.strip() for part in parts)
                value = self.challenge(description)
                variables[name] = value
        # Download the audio.
        full_audio_file = os.path.join(audio_path, '{0}.mp3'.format(host_name))
        if not os.path.exists(full_audio_file) or self.ask('File exists, re-download?'):
            print 'Downloading {0} to {1} (please be patient)'.format(audio_url, full_audio_file)
            urllib.urlretrieve(audio_url, full_audio_file)
        else:
            print 'File already exists, and you wanted to keep it as-is.'
        # Get information about the audio.
        print 'Inspecting MP3 file for total time.'
        try:
            mp3_duration_ms = mp3.duration(full_audio_file)
        except IOError:
            print 'Could not determine duration of MP3 file!'
            return 1
        else:
            print 'MP3 file is {0}ms long'.format(mp3_duration_ms)
        # Prepare the repository.
        print 'Preparing repository.'
        repo = git.Repo.init(repo_path)
        print 'Writing transcription.json file.'
        transcription_json_path = os.path.join(template_path, 'transcription.json')
        if os.path.isfile(transcription_json_path):
            with open(transcription_json_path, 'rU') as f:
                transcription_json = f.read() % variables
        else:
            transcription_json = '{}'
        transcription_json = json.loads(transcription_json)
        transcription_json['audio_url'] = audio_url
        transcription_json['bytes_total'] = os.stat(full_audio_file).st_size
        transcription_json['duration'] = mp3_duration_ms
        transcription_json_output_path = os.path.join(repo_path, 'transcription.json')
        with open(transcription_json_output_path, 'wb') as f:
            json.dump(transcription_json, f, indent=4)
        repo.index.add(['transcription.json'])
        print 'Writing remaining_reviews.json and remaining_snippets.json'
        snippet_ms = snippet_seconds * 1000
        remaining_snippets = range(0, mp3_duration_ms, snippet_ms)
        remaining_reviews = remaining_snippets[:-1]
        remaining_snippets_output_path = os.path.join(repo_path, 'remaining_snippets.json')
        with open(remaining_snippets_output_path, 'wb') as f:
            json.dump(remaining_snippets, f, indent=4)
        repo.index.add(['remaining_snippets.json'])
        remaining_reviews_output_path = os.path.join(repo_path, 'remaining_reviews.json')
        with open(remaining_reviews_output_path, 'wb') as f:
            json.dump(remaining_reviews, f, indent=4)
        repo.index.add(['remaining_reviews.json'])
        print 'Writing additional template files:'
        for template_filename in os.listdir(template_path):
            if template_filename in {'transcription.json', 'variables.txt'}:
                # Skip special files.
                continue
            template_source = os.path.join(template_path, template_filename)
            if os.path.isdir(template_source):
                # Skip directories.
                continue
            print ' - {0}'.format(template_filename)
            with open(template_source, 'rb') as f:
                template_content = f.read() % variables
            template_dest = os.path.join(repo_path, template_filename)
            with open(template_dest, 'wb') as f:
                f.write(template_content)
            repo.index.add([template_filename])
        print 'Initial commit, using your globally configured name and email.'
        repo.index.commit('Initial commit.')
        print 'Done!'
