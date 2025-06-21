from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render
import json
import random
import string
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q, Count
from django.template.loader import render_to_string

from .models import Case
from .forms import CaseForm

class HomePageView(LoginRequiredMixin, ListView):
	model = Case
	template_name = 'home.html'
	context_object_name = 'cases'
	login_url = 'login'
	paginate_by = 10  # Default items per page

	def get_paginate_by(self, queryset):
		return self.request.GET.get('per_page', self.paginate_by)

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
		context['per_page_options'] = [10, 25, 50, 100]
		context['current_per_page'] = self.get_paginate_by(self.object_list)
		return context

	def get(self, request, *args, **kwargs):
		# This will call get_queryset, paginate it, and put the objects in the context
		self.object_list = self.get_queryset()
		context = self.get_context_data()

		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			table_html = render_to_string(
				'partials/_case_table.html',
				{'cases': context['cases']}, # 'cases' is the paginated list
				request=request
			)
			pagination_html = render_to_string(
				'partials/_pagination.html',
				context,
				request=request
			)
			return JsonResponse({'table_html': table_html, 'pagination_html': pagination_html})
		
		return self.render_to_response(context)

class CaseDetailView(LoginRequiredMixin, DetailView):
	model = Case
	template_name = 'cases/caseDetail.html'
	context_object_name = 'case'
	login_url = 'login'

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

def case_detail_view(request, pk):
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
		defect_category_choices = [c[0] for c in Case.DEFECT_CATEGORY_CHOICES]

		for _ in range(20):
			# Decide if this case will have a defect
			has_defect = random.choice([True, False, False]) # Make defects less common
			defect_category = ""
			defect_description = ""
			disposition = ""

			if has_defect:
				# Exclude the empty choice
				non_empty_defect_choices = [c for c in defect_category_choices if c]
				if non_empty_defect_choices:
					defect_category = random.choice(non_empty_defect_choices)
					defect_description = f"不良狀況描述: {defect_category} - {''.join(random.choices(string.ascii_letters + string.digits, k=20))}"
					disposition = f"處置對策: {''.join(random.choices(string.ascii_letters + string.digits, k=15))}"

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
				defect_category=defect_category,
				defect_description=defect_description,
				disposition=disposition,
				inspection_hours=round(Decimal(random.uniform(0.5, 8.0)), 2)
			)
			cases_to_create.append(case)
		
		Case.objects.bulk_create(cases_to_create)
		return JsonResponse({'status': 'success', 'message': '成功新增 20 筆隨機資料！'})
	except Exception as e:
		return JsonResponse({'status': 'error', 'message': f"發生錯誤: {str(e)}"})

@login_required(login_url='login')
def case_pie_chart_view(request):
	start_date_str = request.GET.get('start_date')
	end_date_str = request.GET.get('end_date')

	# Start with the base query
	cases = Case.objects.filter(defect_category__isnull=False).exclude(defect_category__exact='')

	# Apply date filters if provided
	if start_date_str:
		cases = cases.filter(date__gte=start_date_str)
	if end_date_str:
		cases = cases.filter(date__lte=end_date_str)

	# Aggregate data: count cases per defect category
	data = (
		cases.values('defect_category')
		.annotate(count=Count('id'))
		.order_by('-count')
	)

	labels = [item['defect_category'] for item in data]
	counts = [item['count'] for item in data]

	# For AJAX requests, return JSON
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({
			'labels': labels,
			'data': counts,
		})

	# For standard page loads, render the template with context
	context = {
		'labels': json.dumps(labels),
		'data': json.dumps(counts),
		'start_date': start_date_str or '',
		'end_date': end_date_str or '',
	}
	return render(request, 'cases/casePieChart.html', context)
