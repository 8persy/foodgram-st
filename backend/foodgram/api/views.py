from django.db.models import Sum
from django.shortcuts import get_object_or_404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet

from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer,
                          RecipeGetSerializer,
                          UserSubscriptionSerializer,
                          AvatarSerializer,
                          UserSubscribeSerializer, ShoppingCartSerializer)
from .utils import create_model_instance, delete_model_instance
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart)
from users.models import User, Subscription


class PublicUserViewSet(UserViewSet):
    def get_queryset(self):
        users = User.objects.all()
        return users

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_avatar(self, request):
        if request.method == "PUT":
            if 'avatar' not in request.data:
                return Response({"error": "No avatar provided."},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = AvatarSerializer(
                self.request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"avatar": serializer.data["avatar"]},
                status=status.HTTP_200_OK
            )

        else:
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscribeView(APIView):
    """Создание/удаление подписки на пользователя."""

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(user=request.user,
                                           author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(user=request.user.id, author=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsViewSet(mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """Получение списка всех подписок на пользователей."""

    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации об ингредиентах."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами. Создание/изменение/удаление рецепта.
    Получение информации о рецептах.
    Добавление рецептов в избранное и список покупок.
    Отправка файла со списком рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное."""

        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в избранном'
            return delete_model_instance(request,
                                         Favorite, recipe, error_message)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """Работа со списком покупок.
        Удаление/добавление в список покупок."""

        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request,
                                         recipe, ShoppingCartSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в списке покупок'
            return delete_model_instance(request,
                                         ShoppingCart, recipe, error_message)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""

        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
