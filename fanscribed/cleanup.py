import os
import time

from paste.deploy.loadwsgi import loadapp
from paste.script.command import Command


CONTENT_CACHE_THRESHOLD_SECONDS = 48 * 60 * 60 # 48 hours
SNIPPET_CACHE_THRESHOLD_SECONDS = 4 * 60 * 60 # 4 hours


class CleanupCommand(Command):

    min_args = 1
    usage = 'CONFIG_FILE'
    takes_config_file = 1
    summary = 'Clean up generated files'
    description = """\
    This command cleans up generated files that have not been access for more
    than four hours.
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
        cache = settings['fanscribed.cache']
        snippet_cache = settings['fanscribed.snippet_cache']
        # Make sure paths exist.
        if not os.path.isdir(cache):
            print 'Cache path {0} does not exist'.format(cache)
            return 1
        if not os.path.isdir(snippet_cache):
            print 'Snippet cache path {0} does not exist'.format(snippet_cache)
            return 1
        # Go through all of the files in the content cache and delete ones
        # not accessed within the threshold.
        print 'Content cache',
        oldest_allowed = time.time() - CONTENT_CACHE_THRESHOLD_SECONDS
        unlinked_count = 0
        filenames = os.listdir(cache)
        for filename in filenames:
            full_path = os.path.join(cache, filename)
            atime = os.stat(full_path).st_atime
            if atime < oldest_allowed:
                os.unlink(full_path)
                unlinked_count += 1
        print 'Unlinked: {0}, Remaining: {1}'.format(unlinked_count, len(filenames) - unlinked_count)
        # Go through all of the files in the snippet cache and delete ones
        # not accessed within the threshold.
        print 'Snippet cache',
        oldest_allowed = time.time() - SNIPPET_CACHE_THRESHOLD_SECONDS
        unlinked_count = 0
        filenames = os.listdir(snippet_cache)
        for filename in filenames:
            full_path = os.path.join(snippet_cache, filename)
            atime = os.stat(full_path).st_atime
            if atime < oldest_allowed:
                os.unlink(full_path)
                unlinked_count += 1
        print 'Unlinked: {0}, Remaining: {1}'.format(unlinked_count, len(filenames) - unlinked_count)
