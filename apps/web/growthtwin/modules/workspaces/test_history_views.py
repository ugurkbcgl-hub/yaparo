"""Restore endpoint has the same ownership, CSRF and stale-write boundaries."""

import json
from copy import deepcopy

from django.test import Client, TestCase, override_settings

from . import test_document_views
from .creative_documents import save_document


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class HistoryViewTests(TestCase):
    setUp = test_document_views.DocumentViewTests.setUp
    url = test_document_views.DocumentViewTests.url

    def post(self, **changes):
        return self.client.post(
            self.url("restore_scene"),
            json.dumps({"revision": 2, "target_revision": 1} | changes),
            content_type="application/json",
        )

    def test_restore_response_and_stale_replay(self):
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["x"] = 88
        save_document(
            owner=self.owner,
            brand_id=self.brand.pk,
            document_id=self.document.pk,
            expected_revision=1,
            scene=scene,
        )
        response = self.post()
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, response.json()["revision"])
        self.assertEqual(self.document.scene, response.json()["scene"])
        self.assertEqual(3, len(response.json()["history"]))
        self.assertEqual(409, self.post().status_code)

    def test_invalid_payload_csrf_methods_and_other_owner(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(
            403,
            client.post(
                self.url("restore_scene"), "{}", content_type="application/json"
            ).status_code,
        )
        self.assertEqual(405, self.client.get(self.url("restore_scene")).status_code)
        for body, status in (
            ("{}", 400),
            ('{"revision":1,"revision":2,"target_revision":1}', 400),
            (" " * 1001, 413),
        ):
            self.assertEqual(
                status,
                self.client.post(
                    self.url("restore_scene"), body, content_type="application/json"
                ).status_code,
            )
        self.client.force_login(self.other)
        self.assertEqual(404, self.post().status_code)
