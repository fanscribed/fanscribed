from django import forms

from . import models as m


class DefaultTaskForm(forms.ModelForm):

    def save(self, **kwargs):
        task = super(DefaultTaskForm, self).save(False)
        task.submit()
        return task


class TranscribeTaskForm(DefaultTaskForm):

    class Meta:
        model = m.TranscribeTask
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(TranscribeTaskForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True


class StitchTaskForm(DefaultTaskForm):

    class Meta:
        model = m.StitchTask
        exclude = ('transcript', 'is_review', 'state', 'assignee', 'stitch')

    def __init__(self, *args, **kwargs):
        super(StitchTaskForm, self).__init__(*args, **kwargs)
        task = self.instance
        right_sentence_choices = [('-', '(None)')] + [
            (sf.id, sf.text)
            for sf in task.stitch.right.revisions.latest().sentence_fragments.all()
        ]
        for fragment in task.stitch.left.revisions.latest().sentence_fragments.all():
            field_name = 'fragment_{}'.format(fragment.id)
            try:
                pairing = task.pairings.get(left=fragment)
            except m.StitchTaskPairing.DoesNotExist:
                initial = '-'
            else:
                initial = pairing.right.id
            field = forms.ChoiceField(
                choices=right_sentence_choices,
                initial=initial,
                label=fragment.text,
                widget=forms.RadioSelect,
            )
            self.fields[field_name] = field

    def save(self, **kwargs):
        task = self.instance

        for field_name, value in self.cleaned_data.items():
            # Get the left and right sentence fragments chosen by the user.
            left_id = int(field_name.split('_', 1)[1])
            left = task.stitch.left.revisions.latest().sentence_fragments.get(id=left_id)
            if value != '-':
                right_id = int(value)
                right = task.stitch.right.revisions.latest().sentence_fragments.get(id=right_id)
                task.pairings.filter(left=left).delete()
                task.pairings.create(left=left, right=right)
            else:
                # (none) was selected
                pass

        task.submit()
        return task


class CleanTaskForm(DefaultTaskForm):

    class Meta:
        model = m.CleanTask
        fields = ('text',)


class BoundaryTaskForm(DefaultTaskForm):

    class Meta:
        model = m.BoundaryTask
        fields = ('start', 'end')


class SpeakerTaskForm(DefaultTaskForm):

    class Meta:
        model = m.SpeakerTask
        fields = ('speaker', 'new_name')
        widgets = {
            'speaker': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(SpeakerTaskForm, self).__init__(*args, **kwargs)
        self.fields['speaker'].queryset = self.instance.transcript.speakers.all()


TASK_FORM = {
    # task_type: form_class,
    'transcribe': TranscribeTaskForm,
    'stitch': StitchTaskForm,
    'clean': CleanTaskForm,
    'boundary': BoundaryTaskForm,
    'speaker': SpeakerTaskForm,
}
