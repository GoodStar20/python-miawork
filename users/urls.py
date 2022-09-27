from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', views.RestView)

urlpatterns = [
    path('auth/<slug:uw>/', views.AuthView, name = 'user-authenticate'),
    path('profile/', views.UserEditView, name = 'profile'),
    path('api/', include(router.urls), name='api'), ## test is the url
]
