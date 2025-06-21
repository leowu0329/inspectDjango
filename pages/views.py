from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
import random
import string
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q
from django.template.loader import render_to_string

from .models import Case
from .forms import CaseForm

class HomePageView(LoginRequiredMixin, ListView):
	model = Case
	template_name = 'home.html'
	context_object_name = 'cases'
	login_url = 'login'

	def get_queryset(self):
		queryset = super().get_queryset().order_by('-created_at')
		
		query = self.request.GET.get('q')

		if query:
			# Create a Q object to search across multiple fields
			filters = (
				Q(customer__icontains=query) |
				Q(work_order_number__icontains=query) |
				Q(part_number__icontains=query) |
				Q(part_name__icontains=query) |
				Q(inspector__icontains=query) |
				Q(defect_category__icontains=query)
			)
			# Handle date separately if query can be parsed as a date
			try:
				# This is a simple check, more robust parsing might be needed
				from datetime import datetime
				date_query = datetime.strptime(query, '%Y-%m-%d').date()
				filters |= Q(date=date_query)
			except ValueError:
				pass # Not a valid date, ignore

			return queryset.filter(filters)
			
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = CaseForm()
		context['edit_form'] = CaseForm()
		context['search_value'] = self.request.GET.get('q', '')
		return context

	def get(self, request, *args, **kwargs):
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			self.object_list = self.get_queryset()
			context = self.get_context_data()
			html = render_to_string(
				'partials/_case_table.html',
				context,
				request=request
			)
			return JsonResponse({'html': html})
		
		return super().get(request, *args, **kwargs)

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

@require_POST
def add_random_cases(request):
	try:
		cases_to_create = []
		department_choices = [c[0] for c in Case.DEPARTMENT_CHOICES if c[0]]
		inspector_choices = [c[0] for c in Case.INSPECTOR_CHOICES]

		for _ in range(20):
			case = Case(
				inspection_type=random.choice(['首件', '巡檢']),
				sale_type=random.choice(['內銷', '外銷']),
				customer=f"CUST-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}",
				department=random.choice(department_choices),
				date=timezone.now().date() - timedelta(days=random.randint(0, 365)),
				time=timezone.now().time(),
				work_order_number=f"WO-{random.randint(10000, 99999)}",
				operator=f"Operator-{random.randint(1, 10)}",
				drawing_revision=f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
				part_number=f"PN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}",
				part_name=f"Part-{random.choice(['Gear', 'Bolt', 'Nut', 'Plate', 'Shaft'])}",
				quantity=random.randint(1, 1000),
				inspector=random.choice(inspector_choices),
				inspection_hours=round(Decimal(random.uniform(0.5, 8.0)), 2)
			)
			cases_to_create.append(case)
		
		Case.objects.bulk_create(cases_to_create)
		return JsonResponse({'status': 'success', 'message': '成功新增 20 筆隨機資料！'})
	except Exception as e:
		return JsonResponse({'status': 'error', 'message': f"發生錯誤: {str(e)}"})
