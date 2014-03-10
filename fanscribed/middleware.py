from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class LoginRequiredMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        login_required = view_kwargs.pop('login_required', False)
        if login_required and not request.user.is_authenticated():
            return HttpResponseRedirect(
                reverse('account_login')
                + '?next='
                + request.META['PATH_INFO']
            )
