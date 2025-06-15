import base64
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.response import Response
from recipes.models import Ingredient, RecipeIngredient

from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
from django.urls import reverse


def reset_password_request(request):
    """Работа с запросом на обновление пароля"""

    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            reset_url = reverse(
                "reset_password_confirm",
                kwargs={"uidb64": user_id, "token": token}
            )
            reset_link = request.build_absolute_uri(reset_url)
            email_context = render_to_string(
                "password/reset_email.html",
                {
                    "user": user,
                    "reset_link": reset_link,
                }
            )
            send_mail(
                "Сброс пароля",
                email_context,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        return render(request, "password/email.html")
    return render(request, "password/form.html")


def reset_password_confirm(request, uidb64, token):
    """Обновление пароля"""

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=int(user_id))
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password_second')
            if new_password:
                user.set_password(new_password)
                user.save()
                return render(request, "password/success.html")
        return render(
            request,
            "password/confirm.html",
            {"valid_link": True})
    else:
        return render(
            request,
            "password/confirm.html",
            {"valid_link": False}
        )


class Base64ImageField(serializers.ImageField):
    """Вспомогательный класс для работы с изображениями."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def create_ingredients(ingredients, recipe):
    """Вспомогательная функция для добавления ингредиентов.
    Используется при создании/редактировании рецепта."""

    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(Ingredient,
                                               id=ingredient.get('id'))
        amount = ingredient.get('amount')
        ingredient_list.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    RecipeIngredient.objects.bulk_create(ingredient_list)


def create_model_instance(request, instance, serializer_name):
    """Вспомогательная функция для добавления
    рецепта в избранное либо список покупок."""

    serializer = serializer_name(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_name, instance, error_message):
    """Вспомогательная функция для удаления рецепта
    из избранного либо из списка покупок."""

    if not model_name.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    model_name.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
