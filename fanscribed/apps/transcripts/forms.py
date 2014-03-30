from django import forms

from . import models as m


class TranscribeTaskForm(forms.ModelForm):

    class Meta:
        model = m.TranscribeTask
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(TranscribeTaskForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True

    def save(self, **kwargs):
        task = super(TranscribeTaskForm, self).save(False)
        task.submit()
        return task


class StitchTaskForm(forms.ModelForm):

    class Meta:
        model = m.StitchTask
        exclude = ('transcript', 'is_review', 'state', 'assignee',
                   'left', 'right')

    def __init__(self, *args, **kwargs):
        super(StitchTaskForm, self).__init__(*args, **kwargs)
        task = self.instance
        right_sentence_choices = [('-', '(None)')] + [
            (sf.id, sf.text)
            for sf in task.right.sentence_fragments.all()
        ]
        for fragment in task.left.sentence_fragments.all():
            field_name = 'fragment_{}'.format(fragment.id)
            try:
                pairing = task.task_pairings.get(left=fragment)
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
            left = task.left.sentence_fragments.get(id=left_id)
            if value != '-':
                right_id = int(value)
                right = task.right.sentence_fragments.get(id=right_id)
                task.task_pairings.filter(left=left).delete()
                task.task_pairings.create(left=left, right=right)
            else:
                # (none) was selected
                pass

        task.submit()
        return task


TASK_FORM = {
    # task_type: form_class,
    'transcribe': TranscribeTaskForm,
    'stitch': StitchTaskForm,
}
