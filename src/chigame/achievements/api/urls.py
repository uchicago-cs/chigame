from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_achievements),
    path("user-achievements/", views.get_user_achievements),
    path("award-achievement/", views.award_achievement),
    path("award-threshold-achievement/", views.award_threshold_achievement),
]
