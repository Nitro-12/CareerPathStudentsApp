"""
URL configuration for CareerPathStudents project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path
from . import views
from .views import achievement_analytics_api

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('add-achievement/', views.add_achievement, name='add_achievement'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('students/search/', views.student_search, name='student_search'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    # API маршруты
    path('api/achievement_analytics/', achievement_analytics_api, name='achievement_analytics_api'),
    path('generate_recommendations/', views.generate_recommendations, name='generate_recommendations'),
]


