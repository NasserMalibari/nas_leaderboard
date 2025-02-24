from . import views
from django.urls import path
from .views import list_create_participants

urlpatterns = [
    path('competitions/', views.list_create_competition, name='list_create_competition'),
    path('competitions/<int:competition_id>/', views.update_delete_competition, name='update_delete_competition'),
    path('competitions/<int:competition_id>/participants/', list_create_participants, name='participant_list_create'),
    path('competitions/<int:competition_id>/matches/', views.list_create_matches, name='matches'),
    path('competitions/<int:competition_id>/matches/<int:match_id>/', views.update_delete_detail_match, name='update_delete_detail_match'),
    path('competitions/<int:competition_id>/stats/<int:id>/', views.get_stats_detail, name='stats_details'),
    path('competitions/<int:competition_id>/participants/<int:participant_id>/', views.update_delete_participants, name="update_delete_participants")
]

