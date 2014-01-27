import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from waffle.models import Flag, Switch

import yaml


def active_label(switch):
    return 'on' if switch.active else 'off'


def unknown_flags(data):
    names = [x['name'] for x in data.get('flags', [])]
    return Flag.objects.exclude(name__in=names)


def unknown_switches(data):
    names = [x['name'] for x in data.get('switches', [])]
    return Switch.objects.exclude(name__in=names)


class Command(BaseCommand):
    args = "[<filename>]"
    help = "Update waffle flag and switch definitions from this JSON file"

    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError('Too many arguments.')
        self.verbosity = int(options.get('verbosity', 1))

        filename = args[0] if len(args) == 1 else settings.FEATURES_YAML

        try:
            with open(filename) as f:
                data = yaml.load(f) or {}
        except IOError, ioex:
            raise CommandError(os.strerror(ioex.errno))
        except yaml.YAMLError, ex:
            raise CommandError("YAML decoding: " + str(ex))

        for flag_data in data.get('flags', []):
            self.create_or_update_flag(flag_data)

        for flag in unknown_flags(data):
            if self.verbosity >= 1:
                self.stdout.write("Flag '%s' is in the "
                                  "database but NOT in file!\n"
                                  % (flag.name,))

        for switch_data in data.get('switches', []):
            self.create_or_update_switch(switch_data)

        for switch in unknown_switches(data):
            if self.verbosity >= 1:
                self.stdout.write("Switch '%s', which is %s, is in the "
                                  "database but NOT in file!\n"
                                  % (switch.name, switch.active_string))

    def create_or_update_flag(self, flag_data):
        name = flag_data['name']
        note_note = flag_data.get('note', '')
        note_meta = flag_data.get('meta', '')
        initial_superusers = flag_data.get('initial_superusers', False)
        initial_testing = flag_data.get('initial_testing', False)
        everyone = flag_data.get('everyone', None)
        everyone_specified = 'everyone' in flag_data
        if everyone_specified and everyone not in {True, False, None}:
            self.stdout.write(
                'For flag {!r}, "everyone" must be true, false, or null'
                    .format(name))
            everyone_specified = False
        if note_meta:
            note = "{note_note}\nMETA: {note_meta}".format(**locals())
        else:
            note = note_note
        try:
            flag = Flag.objects.get(name=name)
            if self.verbosity >= 1:
                self.stdout.write("Found existing flag '%s'\n" % (name,))
            if flag.note != note:
                flag.note = note
                flag.save()
                if self.verbosity >= 1:
                    self.stdout.write("Updated note (note or meta had "
                                      "changed)\n")
            if everyone_specified and flag.everyone != everyone:
                old_everyone = flag.everyone
                flag.everyone = everyone
                flag.save()
                self.stdout.write(
                    'Updated everyone (changed from {} to {})'
                        .format(old_everyone, everyone))
        except Flag.DoesNotExist:
            flag = Flag.objects.create(
                name=name,
                note=note,
                testing=initial_testing,
                superusers=initial_superusers,
                everyone=everyone if everyone_specified else None,
                )
            if self.verbosity >= 1:
                self.stdout.write("Added flag '%s'\n" % (flag.name,))

    def create_or_update_switch(self, switch_data):
        name = switch_data['name']
        initial_active = switch_data.get('initial_active', False)
        note_note = switch_data.get('note', '')
        note_meta = switch_data.get('meta', '')
        note = "%s\nMETA: %s" % (note_note, note_meta) if note_meta \
            else note_note
        try:
            switch = Switch.objects.get(name=name)
            if self.verbosity >= 1:
                self.stdout.write("Found existing switch '%s', currently "
                                  "%s\n" % (name, switch.active_string))
            if switch.note != note:
                switch.note = note
                switch.save()
                if self.verbosity >= 1:
                    self.stdout.write("Updated note (note or meta had "
                                      "changed)\n")

        except Switch.DoesNotExist:
            switch = Switch.objects.create(name=name,
                                               active=initial_active,
                                               note=note)
            if self.verbosity >= 1:
                self.stdout.write("Added switch '%s', initially %s\n" %
                                  (switch.name, switch.active_string))
