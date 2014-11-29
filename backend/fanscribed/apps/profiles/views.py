from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
import vanilla

from . import forms as f
from . import models as m


class ProfileDetailView(vanilla.DetailView):

    model = m.User  # Line up URL with User pk, not Profile.
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'

    def get_object(self):
        if not self.request.user.is_superuser:
            raise Http404()
        else:
            # Load User, but convert to Profile for template.
            user = super(ProfileDetailView, self).get_object()
            return user.profile


class ProfileUpdateView(vanilla.UpdateView):

    form_class = f.ProfileUpdateForm
    model = m.Profile
    template_name = 'profiles/edit.html'

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        messages.success(self.request, 'Profile changes saved.')
        return reverse('profiles:edit')
