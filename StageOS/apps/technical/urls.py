from rest_framework.routers import DefaultRouter
from .views import (
    TechnicalRiderViewSet, CrewRequirementViewSet, EquipmentRequirementViewSet,
    CueSheetViewSet, CueLineViewSet, PropsItemViewSet, WardrobeItemViewSet,
)

router = DefaultRouter()
router.register('riders', TechnicalRiderViewSet, basename='technical-rider')
router.register('crew', CrewRequirementViewSet, basename='crew-requirement')
router.register('equipment', EquipmentRequirementViewSet, basename='equipment-requirement')
router.register('cue-sheets', CueSheetViewSet, basename='cue-sheet')
router.register('cue-lines', CueLineViewSet, basename='cue-line')
router.register('props', PropsItemViewSet, basename='props-item')
router.register('wardrobe', WardrobeItemViewSet, basename='wardrobe-item')
urlpatterns = router.urls
