import os
import sys

from django.core.management import execute_from_command_line


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'fanscribed.settings.test'

    # Take arguments passed and send them to test runner.
    sys.argv.insert(1, 'test')
    execute_from_command_line(sys.argv)
