from api.filters import TitleFilter
from api.mixins import ModelMixinSet
from api.permissions import (CreateAndUpdatePermission, IsAdmin,
                             IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, MeUserSerializer,
                             ObtainTokenSerializer, ReviewSerializer,
                             TitlesEditorSerializer, TitlesReadSerializer,
                             UserSerializer, UserSignupSerializer)
from api.utils import get_token, send_confirmation_code
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class SignupView(APIView):
    """Регистрация пользователя и получение кода подтверждения."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get_or_create(
                username=serializer.validated_data.get('username'),
                email=serializer.validated_data.get('email')
            )[0]
        except IntegrityError:
            return Response(
                {'Неверный адрес электронной почты или имя пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ObtainTokenView(APIView):
    """Получение токена по имени пользователя и коду подтверждения."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(
                username=serializer.validated_data.get('username')
            )
        except User.DoesNotExist:
            return Response(
                {'username': ['Пользователь не найден']},
                status=status.HTTP_404_NOT_FOUND
            )
        token, token_created = get_token(
            to_check=serializer.validated_data.get('confirmation_code'),
            user=user
        )
        if not token_created:
            return Response(
                {'confirmation_code': ['Неверный код подтверждения']},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'head', 'options', 'post', 'patch', 'delete')

    @action(
        detail=False, methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Управление своей учетной записью."""
        if request.method == 'PATCH':
            serializer = MeUserSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = MeUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoriesViewSet(ModelMixinSet):
    """Получить список всех категорий. Права доступа: Доступно без токена."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenresViewSet(ModelMixinSet):
    """Получить список всех жанров. Права доступа: Доступно без токена."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех объектов. Права доступа: Доступно без токена."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).select_related(
        'category').prefetch_related('genre')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitlesEditorSerializer
        return TitlesReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Пользователи просматривают и оставляют свои отзывы."""
    serializer_class = ReviewSerializer
    permission_classes = (CreateAndUpdatePermission,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all().select_related('author')

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Получить список всех комментариев.
    Добавление нового комментария к отзыву.
    Получить комментарий по id.
    Обновление комментария по id.
    Удаление комментария.
    """
    serializer_class = CommentSerializer
    permission_classes = (CreateAndUpdatePermission,)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
        )

    def get_queryset(self):
        return self.get_review().comments.all().select_related('author')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, review=self.get_review()
        )
