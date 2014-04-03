#!/bin/bash
export DJANGO_SETTINGS_MODULE=fanscribed.settings.test 
export FAST_TEST=1

django-admin.py test fanscribed.apps.transcripts
