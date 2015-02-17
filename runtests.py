import os
import sys

from django.core.management import execute_from_command_line


if __name__ == '__main__':
    test_settings_module = os.environ.setdefault('DJANGO_TEST_SETTINGS_MODULE', 'fanscribed.settings.test')
    os.environ['DJANGO_SETTINGS_MODULE'] = test_settings_module

    # Take arguments passed and send them to test runner.
    sys.argv.insert(1, 'test')
    execute_from_command_line(sys.argv)
