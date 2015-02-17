from .test import *


DATABASE_URL = 'postgres://postgres:@localhost:5432/fanscribed'
DATABASES = {
    'default': parse(DATABASE_URL),
}
