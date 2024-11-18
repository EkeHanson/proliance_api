from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactMessageView


router = DefaultRouter()
router.register(r'contact', ContactMessageView)


urlpatterns = [
    path('', include(router.urls)),
]

