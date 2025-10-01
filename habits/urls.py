from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', LoginView, name="login"),
    path('logout/', LogoutView, name="logout"),
    path('dashboard/', dashboard, name='dashboard'),
    path('signup/', signup_view, name='signup'),
    path('habit/add/', habit_create, name='habit_add'),
    path('habit/<int:pk>/edit/', habit_update, name='habit_edit'),
    path('habit/<int:pk>/delete/', habit_delete, name='habit_delete'),
    path('ajax/mark-complete/', mark_complete, name='mark_complete'),
    path('leaderboard/', leaderboard, name='leaderboard'),

]