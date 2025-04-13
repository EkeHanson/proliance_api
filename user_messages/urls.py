# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ContactMessageView, QuoteRequestView, DemoRequestView

# router = DefaultRouter()
# router.register(r'contact', ContactMessageView)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('quote-requests/', QuoteRequestView.as_view({'post': 'create'}), name='quote-request'),
#     path('demo-requests/', DemoRequestView.as_view({'post': 'create'}), name='demo-request'),
# ]
from django.urls import path
from .views import (
    ContactMessageView, ContactMessageListView, ContactMessageDetailView,
    QuoteRequestView, QuoteRequestListView, QuoteRequestDetailView,
    DemoRequestView, DemoRequestListView, DemoRequestDetailView
)
from django.urls import path
from .views import get_ga_data

urlpatterns = [
    #Google Page info
    path('api/analytics/', get_ga_data, name='get_ga_data'),
    # Contact Message URLs
    path('contact-messages/', ContactMessageView.as_view({'post': 'create'})),
    path('contact-messages/list/', ContactMessageListView.as_view()),
    path('contact-messages/<int:id>/', ContactMessageDetailView.as_view()),
    
    # Quote Request URLs
    path('quote-requests/', QuoteRequestView.as_view({'post': 'create'})),
    path('quote-requests/list/', QuoteRequestListView.as_view()),
    path('quote-requests/<int:id>/', QuoteRequestDetailView.as_view()),
    
    # Demo Request URLs
    path('demo-requests/', DemoRequestView.as_view({'post': 'create'})),
    path('demo-requests/list/', DemoRequestListView.as_view()),
    path('demo-requests/<int:id>/', DemoRequestDetailView.as_view()),
]