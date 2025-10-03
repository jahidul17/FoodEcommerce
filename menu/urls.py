from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, FoodItemViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'foods', FoodItemViewSet)

urlpatterns = router.urls
