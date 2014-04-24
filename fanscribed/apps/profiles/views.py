from django.contrib import messages
from django.core.urlresolvers import reverse
import vanilla

from . import forms as f
from . import models as m


class ProfileUpdateView(vanilla.UpdateView):

    form_class = f.ProfileUpdateForm
    model = m.Profile
    template_name = 'profiles/edit.html'

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        messages.success(self.request, 'Profile changes saved.')
        return reverse('profiles:edit')
