# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import LicenseKey
from .serializers import LicenseKeySerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import Lower

# views.py
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LicenseKeySearchView(generics.ListAPIView):
    serializer_class = LicenseKeySerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = LicenseKey.objects.all()
        organization_name = self.request.query_params.get('organization_name', '').strip().lower()
        application_name = self.request.query_params.get('application_name', '').strip().lower()
        
        if organization_name:
            # First try simple icontains
            initial_matches = queryset.filter(
                organization_name__icontains=organization_name
            )
            
            if not initial_matches.exists():
                # Fallback to more flexible search
                queryset = queryset.annotate(
                    lower_org=Lower('organization_name')
                ).filter(
                    lower_org__contains=organization_name
                )
            else:
                queryset = initial_matches
        
        if application_name:
            queryset = queryset.filter(
                application_name__icontains=application_name
            )
            
        return queryset 
class LicenseKeyListCreateView(generics.ListCreateAPIView):
    queryset = LicenseKey.objects.all()
    serializer_class = LicenseKeySerializer
    pagination_class = StandardResultsSetPagination

class LicenseKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LicenseKey.objects.all()
    serializer_class = LicenseKeySerializer

class ValidateLicenseView(generics.GenericAPIView):
    serializer_class = LicenseKeySerializer
    
    def post(self, request):
        license_key = request.data.get('license_key')
        application_url = request.data.get('application_url')
        
        try:
            license = LicenseKey.objects.get(
                key=license_key,
                application_url=application_url
            )
            
            response_data = {
                'valid': license.is_valid,
                'organization_name': license.organization_name,
                'application_name': license.application_name,
                'expiry_date': license.expiry_date
            }
            
            if not license.is_valid:
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)
                
            return Response(response_data)
            
        except LicenseKey.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'License not found'},
                status=status.HTTP_404_NOT_FOUND
            )