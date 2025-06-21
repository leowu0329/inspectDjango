from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Case
from .forms import CaseForm

class HomePageView(LoginRequiredMixin, ListView):
	model = Case
	template_name = 'home.html'
	context_object_name = 'cases'
	login_url = 'login'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = CaseForm()
		return context

@require_POST
def create_case(request):
	form = CaseForm(request.POST)
	if form.is_valid():
		form.save()
		return JsonResponse({'status': 'success', 'message': '案例新增成功！'})
	else:
		# 將表單錯誤轉換為更易於處理的格式
		errors = {field: error[0] for field, error in form.errors.items()}
		return JsonResponse({'status': 'error', 'errors': errors})
