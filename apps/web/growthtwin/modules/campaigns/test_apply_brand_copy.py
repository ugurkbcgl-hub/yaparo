"""Explicit candidate application preserves scene/history and refuses stale forms."""

from copy import deepcopy
from dataclasses import asdict
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.ai_gateway.brand_tasks import digest
from growthtwin.modules.workspaces.models import Brand, Workspace

from .apply_brand_copy import apply_brand_copy
from .brand_copy import preview_brand_copy
from .test_design_selection import SelectionFixture


class ApplyFixture(SelectionFixture):
    def setUp(self):
        super().setUp()
        self.select()
        task, result = preview_brand_copy(
            owner=self.owner, draft_id=self.draft.pk, selection_version=1
        )
        self.candidate = result.creative_result.variants[0]
        self.payload = dict(
            task_id=task.task_id,
            request_fingerprint=task.fingerprint,
            candidate_key=self.candidate.key,
            candidate_digest=digest(asdict(self.candidate)),
            expected_revision=1,
            fields="title",
        )

    def apply(self, **changes):
        return apply_brand_copy(
            owner=self.owner,
            draft_id=self.draft.pk,
            selection_version=1,
            **(self.payload | changes),
        )


@override_settings(
    DEBUG=True,
    SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True,
    SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED=True,
    SYNTHETIC_BRAND_COPY_APPLY_ENABLED=True,
)
class ApplyCopyTests(ApplyFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.url = reverse("campaigns:brand_copy_apply", args=[self.draft.pk, 1])

    def post(self, payload=None, client=None):
        return (client or self.client).post(
            self.url,
            urlencode(payload or self.payload),
            content_type="application/x-www-form-urlencoded",
        )

    def test_title_only_new_revision_preserves_other_scene_fields_and_selection(self):
        before = deepcopy(self.document.scene)
        expected = deepcopy(before)
        expected["layers"][2]["text"] = self.candidate.headline
        document = self.apply()
        self.assertEqual(document.revision, 2)
        self.assertEqual(document.scene, expected)
        self.assertEqual(document.history.get(revision=1).scene, before)
        self.assertEqual(document.history.count(), 2)
        self.assertEqual(self.draft.design_choices.count(), 1)
        self.assertEqual(self.draft.design_choices.first().snapshot.revision, 1)
        with self.assertRaises(ValidationError):
            self.apply()
        self.assertEqual(document.history.count(), 2)

    def test_title_and_subtitle_exact_no_truncation(self):
        document = self.apply(fields="title_subtitle")
        self.assertEqual(document.scene["layers"][2]["text"], self.candidate.headline)
        self.assertEqual(document.scene["layers"][3]["text"], self.candidate.body)

    def test_oversize_subtitle_refuses_without_partial_title(self):
        task, result = preview_brand_copy(
            owner=self.owner,
            draft_id=self.draft.pk,
            selection_version=1,
            task_id=self.payload["task_id"],
        )
        long = next(
            row for row in result.creative_result.variants if len(row.body) > 100
        )
        with self.assertRaises(ValidationError):
            self.apply(
                candidate_key=long.key,
                candidate_digest=digest(asdict(long)),
                fields="title_subtitle",
            )
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 1)
        self.assertEqual(self.document.history.count(), 1)

    def test_saved_edit_selection_change_and_forged_candidate_refuse(self):
        before = deepcopy(self.document.scene)
        changed = deepcopy(before)
        changed["layers"][2]["text"] = "User edit"
        self.save(changed)
        with self.assertRaises(ValidationError):
            self.apply()
        self.document.refresh_from_db()
        self.assertEqual(self.document.scene, changed)
        with self.assertRaises(ValidationError):
            self.apply(expected_revision=2, candidate_digest="0" * 64)
        self.select(
            expected_document_revision=2,
            expected_selection_version=1,
            request_id=uuid4(),
        )
        with self.assertRaises(ValidationError):
            self.apply(expected_revision=2)
        self.assertEqual(self.document.history.count(), 2)

    def test_write_boundary_selection_change_rolls_back(self):
        from growthtwin.modules.campaigns import apply_brand_copy as service

        original = service._write_document

        def before(*args, **kwargs):
            self.select(expected_selection_version=1, request_id=uuid4())
            return original(*args, **kwargs)

        with patch.object(service, "_write_document", side_effect=before):
            with self.assertRaises(ValidationError):
                self.apply()
        self.document.refresh_from_db()
        self.assertEqual(self.document.revision, 1)
        self.assertEqual(self.document.history.count(), 1)
        self.assertEqual(
            self.draft.design_choices.count(), 1
        )  # Same transaction mutation rolled back.

    def test_http_csrf_closed_fields_duplicates_and_private_errors(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.owner)
        self.assertEqual(self.post(client=strict).status_code, 403)
        self.assertEqual(
            self.post(self.payload | {"headline": "caller text"}).status_code, 409
        )
        duplicated = urlencode(self.payload) + "&fields=title_subtitle"
        self.assertEqual(
            self.client.post(
                self.url, duplicated, content_type="application/x-www-form-urlencoded"
            ).status_code,
            409,
        )
        response = self.post()
        self.assertEqual(response.status_code, 302)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.post().status_code, 409)

    def test_scope_flags_get_and_preparse_multipart_refuse(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        for options in (
            {"DEBUG": False},
            {"SYNTHETIC_BRAND_COPY_APPLY_ENABLED": False},
            {"SYNTHETIC_BRAND_COPY_PREVIEW_ENABLED": False},
            {"SYNTHETIC_CAMPAIGN_DESIGN_ENABLED": False},
        ):
            with self.settings(**options):
                self.assertEqual(self.post().status_code, 404)
        self.client.force_login(self.other)
        self.assertEqual(self.post().status_code, 404)
        self.client.force_login(self.owner)
        other = Workspace.objects.create(owner=self.owner, name="Other")
        Brand.objects.filter(pk=self.brand.pk).update(workspace=other)
        self.assertEqual(self.post().status_code, 404)
        for url in (self.url, self.url.replace("/1/", "/01/")):
            with patch.object(
                HttpRequest,
                "_load_post_and_files",
                side_effect=AssertionError("No intake"),
            ):
                response = self.client.post(url, {"file": "synthetic"})
            self.assertEqual(response.status_code, 415)
            self.assertIn("no-store", response["Cache-Control"])
