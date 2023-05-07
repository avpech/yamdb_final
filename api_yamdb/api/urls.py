from api.views import ObtainTokenView, SignupView
from django.urls import include, path
from rest_framework import routers

from .views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('categories', CategoriesViewSet, 'categories')
router.register('genres', GenresViewSet, 'genres')
router.register('titles', TitleViewSet, 'titles')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, 'reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, 'comments'
)
router.register(r'users', UserViewSet, 'users')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/', ObtainTokenView.as_view(), name='obtain_token'),
]
