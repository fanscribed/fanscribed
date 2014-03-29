from django import forms

from .models import TranscriptionTask


class TranscriptionTaskForm(forms.ModelForm):

    class Meta:
        fields = ('text',)
        model = TranscriptionTask

    def __init__(self, *args, **kwargs):
        super(TranscriptionTaskForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True

    def save(self, **kwargs):
        task = super(TranscriptionTaskForm, self).save(False)
        task.submit()
        return task


TASK_FORM = {
    # task_type: form_class,
    'transcribe': TranscriptionTaskForm,
}
