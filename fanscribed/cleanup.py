import os
import time

from paste.deploy.loadwsgi import loadapp
from paste.script.command import Command


THRESHOLD_SECONDS = 4 * 60 * 60 # 4 hours


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
        snippet_cache = settings['fanscribed.snippet_cache']
        # Make sure paths exist.
        if not os.path.isdir(snippet_cache):
            print 'Snippet cache path {0} does not exist'.format(snippet_cache)
            return 1
        # Go through all of the files in the snippet cache and delete ones
        # not accessed within the threshold.
        oldest_allowed = time.time() - THRESHOLD_SECONDS
        unlinked_count = 0
        filenames = os.listdir(snippet_cache)
        for filename in filenames:
            full_path = os.path.join(snippet_cache, filename)
            atime = os.stat(full_path).st_atime
            if atime < oldest_allowed:
                os.unlink(full_path)
                unlinked_count += 1
        print 'Unlinked: {0}, Remaining: {1}'.format(unlinked_count, len(filenames) - unlinked_count)
