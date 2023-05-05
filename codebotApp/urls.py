from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('suggest/', views.suggest, name='suggest'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('past/', views.past, name='past'),
    #path('openai_api/', views.openai_api, name='openai_api'),
    path('delete/<list_id>', views.delete, name='delete'),
]
