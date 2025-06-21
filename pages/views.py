from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json

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
		# For Edit Modal
		context['edit_form'] = CaseForm()
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

def case_detail(request, pk):
	case = get_object_or_404(Case, pk=pk)
	data = {
		'inspection_type': case.inspection_type,
		'sale_type': case.sale_type,
		'customer': case.customer,
		'department': case.department,
		'date': case.date,
		'time': case.time,
		'work_order_number': case.work_order_number,
		'operator': case.operator,
		'drawing_revision': case.drawing_revision,
		'part_number': case.part_number,
		'part_name': case.part_name,
		'quantity': case.quantity,
		'inspector': case.inspector,
		'defect_category': case.defect_category,
		'defect_description': case.defect_description,
		'disposition': case.disposition,
		'inspection_hours': str(case.inspection_hours),
	}
	return JsonResponse(data)

@require_POST
def update_case(request, pk):
	case = get_object_or_404(Case, pk=pk)
	form = CaseForm(request.POST, instance=case)
	if form.is_valid():
		form.save()
		return JsonResponse({'status': 'success', 'message': '案例更新成功！'})
	else:
		errors = {field: error[0] for field, error in form.errors.items()}
		return JsonResponse({'status': 'error', 'errors': errors})

@require_POST
def delete_case(request, pk):
	try:
		case = get_object_or_404(Case, pk=pk)
		case.delete()
		return JsonResponse({'status': 'success', 'message': '案例刪除成功！'})
	except Exception as e:
		return JsonResponse({'status': 'error', 'message': str(e)})
