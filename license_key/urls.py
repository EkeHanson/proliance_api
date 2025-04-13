# urls.py
from django.urls import path
from .views import (
    LicenseKeyListCreateView, LicenseKeyDetailView, LicenseKeySearchView, ValidateLicenseView
)

urlpatterns = [
    path('licenses/', LicenseKeyListCreateView.as_view(), name='license-list-create'),
    path('licenses/<int:pk>/', LicenseKeyDetailView.as_view(), name='license-detail'),
    path('validate/', ValidateLicenseView.as_view(), name='validate-license'),
    path('licenses/search/', LicenseKeySearchView.as_view(), name='license-search'),
]