from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def health(request):
    return JsonResponse({'status': 'ok', 'version': 'sprint-0'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/v1/', include([
        path('', include('apps.accounts.urls')),
        path('', include('apps.organisations.urls')),
        path('', include('apps.audit.urls')),
        path('', include('apps.structure.urls')),
        path('', include('apps.contexts.urls')),
        path('', include('apps.tasks.urls')),
        path('', include('apps.documents.urls')),
        path('', include('apps.workflows.urls')),
        path('', include('apps.approvals.urls')),
        path('programming/', include('apps.programming.urls')),
        path('marketing/', include('apps.marketing.urls')),
        path('technical/', include('apps.technical.urls')),
        path('operations/', include('apps.operations.urls')),
        path('contracts/', include('apps.contracts.urls')),
        path('suppliers/', include('apps.suppliers.urls')),
        path('artists/', include('apps.artists.urls')),
        path('youth/', include('apps.youth.urls')),
        path('ticketing/', include('apps.ticketing.urls')),
        path('governance/', include('apps.governance.urls')),
        path('reports/', include('apps.reports.urls')),
        path('integrations/', include('apps.integrations.urls')),
    ])),
]
