from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowTemplateViewSet, WorkflowStepTemplateViewSet,
    WorkflowInstanceViewSet, WorkflowStepInstanceViewSet,
)

router = DefaultRouter()
router.register('workflows/templates', WorkflowTemplateViewSet, basename='workflow-template')
router.register('workflows/step-templates', WorkflowStepTemplateViewSet, basename='workflow-step-template')
router.register('workflows/instances', WorkflowInstanceViewSet, basename='workflow-instance')
router.register('workflows/steps', WorkflowStepInstanceViewSet, basename='workflow-step')

urlpatterns = router.urls
