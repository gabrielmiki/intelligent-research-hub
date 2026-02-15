"""
URL configuration for intelliresearchhub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from interface_layer import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add Django's built-in auth URLs (Login/Logout/Password Reset)
    path('accounts/', include('django.contrib.auth.urls')),
    # Enables the "Log in" button in the API interface
    path('api-auth/', include('rest_framework.urls')),
    path('summarize/', views.make_summary_request, name='submit-summary'),
    path('summarize/<uuid:summary_id>/', views.get_summary_status, name='get-summary-detail'),
    path('my-summaries/', views.get_summaries, name='list-summaries'),

    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'), # Your frontend from before
]
