from rest_framework.routers import DefaultRouter
from .views import GLAccountViewSet, GLJournalEntryViewSet, DeferredIncomeViewSet

router = DefaultRouter()
router.register('accounts', GLAccountViewSet, basename='gl-account')
router.register('journals', GLJournalEntryViewSet, basename='gl-journal')
router.register('deferred-income', DeferredIncomeViewSet, basename='deferred-income')

urlpatterns = router.urls
