from rest_framework.routers import DefaultRouter
from .views import (
    YouthProjectViewSet, ActivityViewSet, SessionViewSet, LearnerGroupViewSet,
    FacilitatorAssignmentViewSet, ConsentRecordViewSet, AttendanceRecordViewSet,
    AssessmentViewSet, ShowcaseOutputViewSet,
)

router = DefaultRouter()
router.register('projects', YouthProjectViewSet, basename='youth-project')
router.register('activities', ActivityViewSet, basename='youth-activity')
router.register('sessions', SessionViewSet, basename='youth-session')
router.register('learner-groups', LearnerGroupViewSet, basename='learner-group')
router.register('facilitators', FacilitatorAssignmentViewSet, basename='facilitator-assignment')
router.register('consent', ConsentRecordViewSet, basename='consent-record')
router.register('attendance', AttendanceRecordViewSet, basename='attendance-record')
router.register('assessments', AssessmentViewSet, basename='youth-assessment')
router.register('showcases', ShowcaseOutputViewSet, basename='showcase-output')
urlpatterns = router.urls
