from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet, DepartmentViewSet, CategoryViewSet

router = DefaultRouter()

router.register(r'complaints', ComplaintViewSet, basename= 'complaint')
router.register("departments", DepartmentViewSet, basename="department")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls