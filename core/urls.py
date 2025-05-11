from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/google/accounts/', include('allauth.urls')),

    # # Your other API routes
    # path('api/user_messages/', include('user_messages.urls')),
    path('api/users/', include('users.urls')),
    path('api/user_messages/', include('user_messages.urls')),
    path('api/license_key/', include('license_key.urls')),
    path('api/issues_log/', include('issues_log.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
