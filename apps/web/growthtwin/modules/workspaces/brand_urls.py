"""Explicit brand routes without global selected-brand session state."""

from django.urls import path

from growthtwin.modules.assets import views as asset_views
from growthtwin.modules.workspaces import (
    brand_views,
    hosted_ad_views,
    hosted_image_views,
    hosted_trial_views,
)

app_name = "brands"
urlpatterns = [
    path("", brand_views.brand_list, name="list"),
    path("ai-trial/", hosted_trial_views.preview, name="hosted_trial"),
    path("ai-trial/drafts/", hosted_ad_views.choices, name="hosted_ad_choices"),
    path("ai-trial/drafts/create/", hosted_ad_views.create, name="hosted_ad_create"),
    path(
        "ai-trial/drafts/<uuid:draft_id>/",
        hosted_ad_views.editor,
        name="hosted_ad_editor",
    ),
    path(
        "ai-trial/drafts/<uuid:draft_id>/save/",
        hosted_ad_views.save,
        name="hosted_ad_save",
    ),
    path(
        "ai-trial/drafts/<uuid:draft_id>/revisions/<int:revision>/package.json",
        hosted_ad_views.package,
        name="hosted_ad_package",
    ),
    path(
        "ai-trial/drafts/<uuid:draft_id>/image/",
        hosted_ad_views.image,
        name="hosted_ad_image",
    ),
    path("ai-trial/image/", hosted_image_views.preview, name="hosted_image_trial"),
    path(
        "ai-trial/image/generate/",
        hosted_image_views.generate,
        name="hosted_image_generate",
    ),
    path(
        "ai-trial/image/content/",
        hosted_image_views.content,
        name="hosted_image_content",
    ),
    path(
        "ai-trial/image/download/",
        hosted_image_views.content,
        {"download": True},
        name="hosted_image_download",
    ),
    path(
        "ai-trial/generate/",
        hosted_trial_views.generate,
        name="hosted_trial_generate",
    ),
    path("new/", brand_views.brand_create, name="create"),
    path("prepare/", brand_views.prepare_workspace, name="prepare"),
    path(
        "<int:brand_id>/materials/prepare/",
        asset_views.material_prepare,
        name="materials_prepare",
    ),
    path("<int:brand_id>/", brand_views.brand_detail, name="detail"),
    path(
        "<int:brand_id>/materials/generate/",
        asset_views.palette_generate,
        name="palette_generate",
    ),
    path(
        "<int:brand_id>/materials/<uuid:material_id>/image/",
        asset_views.palette_image,
        name="palette_image",
    ),
    path("<int:brand_id>/edit/", brand_views.brand_edit, name="edit"),
]
