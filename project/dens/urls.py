from django.urls import path
from django.contrib.auth.views import LoginView

from .views import register_view, logout_view, index_view, den_view, profile_view, password_view, email_view, delete_view

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('', index_view, name='index'),
    path('den/<str:den_slug>/', den_view, name='den'),
    path('profile/', profile_view, name='profile'),
    path('profile/password/', password_view, name='password'),
    path('profile/email/', email_view, name='email'),
    path('profile/delete/', delete_view, name='delete')
]
