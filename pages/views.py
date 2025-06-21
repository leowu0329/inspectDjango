from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Case

class HomePageView(LoginRequiredMixin, ListView):
	model = Case
	template_name = 'home.html'
	context_object_name = 'cases'
	login_url = 'login'
