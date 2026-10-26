"""Authenticated local campaign planning routes."""

from django.urls import path

from growthtwin.modules.campaigns import (
    brand_ad_views,
    brand_copy_views,
    design_views,
    hosted_ad_views,
    preview_views,
    views,
)

app_name = "campaigns"

urlpatterns = [
    path(
        "<int:draft_id>/brand-creative/", brand_ad_views.choose, name="brand_ad_choose"
    ),
    path(
        "<int:draft_id>/brand-creative/<int:selection_version>/preview/",
        brand_ad_views.preview,
        name="brand_ad_preview",
    ),
    path(
        "<int:draft_id>/brand-creative/<int:selection_version>/image/",
        brand_ad_views.image,
        name="brand_ad_image",
    ),
    path(
        "<int:draft_id>/ai-visual/<int:selection_version>/package.json",
        hosted_ad_views.package,
        name="hosted_ad_package",
    ),
    path("<int:draft_id>/ai-visual/", hosted_ad_views.choose, name="hosted_ad_choose"),
    path(
        "<int:draft_id>/ai-visual/<int:selection_version>/preview/",
        hosted_ad_views.preview,
        name="hosted_ad_preview",
    ),
    path(
        "<int:draft_id>/ai-visual/<int:selection_version>/image/",
        hosted_ad_views.image,
        name="hosted_ad_image",
    ),
    path(
        "<int:draft_id>/design/<int:selection_version>/copy/apply/",
        brand_copy_views.apply_copy,
        name="brand_copy_apply",
    ),
    path(
        "<int:draft_id>/design/<int:selection_version>/copy/",
        brand_copy_views.brand_copy,
        name="brand_copy",
    ),
    path(
        "<int:draft_id>/design/<int:selection_version>/bundle/",
        preview_views.bundle,
        name="design_bundle",
    ),
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
