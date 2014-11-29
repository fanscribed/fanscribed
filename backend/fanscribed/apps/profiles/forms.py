from django import forms

from . import models as m


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = m.Profile
        fields = ('task_types', 'wants_reviews', 'task_order')
        widgets = {
            'task_types': forms.CheckboxSelectMultiple,
            'task_order': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
