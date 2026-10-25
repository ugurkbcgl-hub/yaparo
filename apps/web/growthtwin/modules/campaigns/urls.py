"""Authenticated local campaign planning routes."""

from django.urls import path

from growthtwin.modules.campaigns import design_views, preview_views, views

app_name = "campaigns"

urlpatterns = [
    path(
        "<int:draft_id>/design/<int:selection_version>/preview/",
        preview_views.preview,
        name="design_preview",
    ),
    path(
        "<int:draft_id>/design/<int:selection_version>/image/",
        preview_views.image,
        name="design_image",
    ),
    path("<int:draft_id>/design/", design_views.campaign_design, name="design"),
    path("", views.campaign_list, name="list"),
    path("new/", views.campaign_create, name="create"),
    path("<int:draft_id>/", views.campaign_detail, name="detail"),
    path("<int:draft_id>/journey/", views.campaign_journey_overview, name="journey"),
    path("<int:draft_id>/download/", views.campaign_download, name="download"),
    path("<int:draft_id>/rehearsal/", views.campaign_rehearsal, name="rehearsal"),
    path("<int:draft_id>/report/", views.campaign_report, name="report"),
    path("<int:draft_id>/edit/", views.campaign_edit, name="edit"),
    path(
        "<int:draft_id>/creatives/generate/",
        views.campaign_generate_creatives,
        name="generate_creatives",
    ),
    path(
        "<int:draft_id>/creatives/preference/",
        views.campaign_select_preferred_creative,
        name="select_preferred_creative",
    ),
    path(
        "<int:draft_id>/creatives/edit/",
        views.campaign_edit_creative,
        name="edit_creative",
    ),
    path(
        "<int:draft_id>/creatives/restore/",
        views.campaign_restore_creative,
        name="restore_creative",
    ),
    path("<int:draft_id>/delete/", views.campaign_delete, name="delete"),
]
