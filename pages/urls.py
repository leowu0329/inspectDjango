from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomePageView.as_view(), name='home'),
	path('case/create/', views.create_case, name='create_case'),
]