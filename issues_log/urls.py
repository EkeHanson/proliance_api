
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, IssueViewSet, CommentViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'issues', IssueViewSet, basename='issu es')
router.register(r'issues/(?P<issue_pk>[^/.]+)/comments', CommentViewSet, basename='comments')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]

