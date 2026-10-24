"""Explicit brand and UUID document scopes; no global selection."""

from django.urls import path

from growthtwin.modules.workspaces import document_views, editor_views

app_name = "brand_documents"
urlpatterns = [
    path(
        "<uuid:document_id>/restore/", editor_views.restore_scene, name="restore_scene"
    ),
    path("<uuid:document_id>/editor/", editor_views.editor, name="editor"),
    path("<uuid:document_id>/scene/", editor_views.save_scene, name="save_scene"),
    path("create/", document_views.document_create, name="create"),
    path("<uuid:document_id>/", document_views.document_detail, name="detail"),
    path(
        "<uuid:document_id>/download/",
        document_views.document_download,
        name="download",
    ),
]
