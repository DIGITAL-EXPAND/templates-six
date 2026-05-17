from rest_framework.routers import DefaultRouter
from .views import TechnicalRiderViewSet, CrewRequirementViewSet, EquipmentRequirementViewSet

router = DefaultRouter()
router.register('riders', TechnicalRiderViewSet, basename='technical-rider')
router.register('crew', CrewRequirementViewSet, basename='crew-requirement')
router.register('equipment', EquipmentRequirementViewSet, basename='equipment-requirement')
urlpatterns = router.urls
