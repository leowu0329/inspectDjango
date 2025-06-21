from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomePageView.as_view(), name='home'),
	path('case/create/', views.create_case, name='create_case'),
	path('case/<int:pk>/', views.case_detail, name='case_detail'),
	path('case/<int:pk>/update/', views.update_case, name='update_case'),
	path('case/<int:pk>/delete/', views.delete_case, name='delete_case'),
]