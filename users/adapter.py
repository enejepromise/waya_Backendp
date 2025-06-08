from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class WayaAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user

        if user.role == 'parent':
            return resolve_url('/parent/dashboard')

        elif user.role == 'child':
            return resolve_url('/child/dashboard')

        return resolve_url('/')
