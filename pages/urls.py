from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomePageView.as_view(), name='home'),
	path('case/create/', views.create_case, name='create_case'),
	path('case/<int:pk>/', views.case_detail_view, name='case_detail'),
	path('case/<int:pk>/update/', views.update_case, name='update_case'),
	path('case/<int:pk>/delete/', views.delete_case, name='delete_case'),
	path('case/add-random/', views.add_random_cases, name='add_random_cases'),
	path('case/detail/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail_page'),
]