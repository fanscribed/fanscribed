import os

from .test import *


DATABASE_URL = 'postgres://postgres:@localhost:5432/fanscribed'
DATABASES = {
    'default': parse(DATABASE_URL),
}

os.makedirs('_temp')
TRANSCRIPT_PROCESSING_TEMP_DIR = os.path.abspath('_temp')
