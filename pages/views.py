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
		queryset = super().get_queryset()
		
		# Get search, filter, and ordering parameters
		query = self.request.GET.get('q')
		ordering = self.request.GET.get('ordering', '-date')
		inspection_type = self.request.GET.get('inspection_type')
		sale_type = self.request.GET.get('sale_type')
		department = self.request.GET.get('department')
		inspector = self.request.GET.get('inspector')

		filters = Q()

		# Apply text search query
		if query:
			query_filters = (
				Q(customer__icontains=query) |
				Q(work_order_number__icontains=query) |
				Q(part_number__icontains=query) |
				Q(part_name__icontains=query) |
				Q(inspector__icontains=query) |
				Q(defect_category__icontains=query)
			)
			try:
				from datetime import datetime
				date_query = datetime.strptime(query, '%Y-%m-%d').date()
				query_filters |= Q(date=date_query)
			except ValueError:
				pass
			filters &= query_filters
		
		# Apply dropdown filters
		if inspection_type:
			filters &= Q(inspection_type=inspection_type)
		if sale_type:
			filters &= Q(sale_type=sale_type)
		if department:
			filters &= Q(department=department)
		if inspector:
			filters &= Q(inspector=inspector)
			
		queryset = queryset.filter(filters)
			
		if ordering in ['date', '-date']:
			queryset = queryset.order_by(ordering)
			
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = CaseForm()
		context['edit_form'] = CaseForm()
		context['search_value'] = self.request.GET.get('q', '')
		context['current_ordering'] = self.request.GET.get('ordering', '-date')
		
		# Pass choices and current filter values to template
		context['inspection_type_choices'] = Case.INSPECTION_TYPE_CHOICES
		context['sale_type_choices'] = Case.SALE_TYPE_CHOICES
		context['department_choices'] = Case.DEPARTMENT_CHOICES
		context['inspector_choices'] = Case.INSPECTOR_CHOICES
		context['filter_values'] = {
			'inspection_type': self.request.GET.get('inspection_type', ''),
			'sale_type': self.request.GET.get('sale_type', ''),
			'department': self.request.GET.get('department', ''),
			'inspector': self.request.GET.get('inspector', ''),
		}
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
