from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    UserSubscribeView,
                    UserSubscriptionsViewSet,
                    PublicUserViewSet,
                    UserInfoView,
                    UserRecipesView)

router = DefaultRouter()

router.register('ingredients',
                IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', PublicUserViewSet, basename='user')

urlpatterns = [
    path('users/subscriptions/',
         UserSubscriptionsViewSet.as_view({'get': 'list'})),
    path('users/<int:user_id>/subscribe/', UserSubscribeView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/info/', UserInfoView.as_view(), name='user-info'),
    path('users/<int:id>/recipes/', UserRecipesView.as_view(), name='user-recipes'),
]
