"""Focused HTTP guards for saved visual scenes."""

import json
from copy import deepcopy

from django.test import Client, TestCase, override_settings

from . import test_document_views


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class EditorViewTests(TestCase):
    setUp = test_document_views.DocumentViewTests.setUp
    url = test_document_views.DocumentViewTests.url

    def post(self, payload):
        return self.client.post(
            self.url("save_scene"), json.dumps(payload), content_type="application/json"
        )

    def test_open_bootstrap_and_save_noop_stale(self):
        response = self.client.get(self.url("editor"))
        self.assertContains(response, "editor-data")
        self.assertIn("script-src 'self'", response["Content-Security-Policy"])
        self.assertIn("no-store", response["Cache-Control"])
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["x"] = 78
        self.assertEqual(
            self.post({"revision": 1, "scene": scene}).json(), {"revision": 2}
        )
        self.assertEqual(self.post({"revision": 1, "scene": scene}).status_code, 409)
        self.assertEqual(
            self.post({"revision": 2, "scene": scene}).json(), {"revision": 2}
        )

    def test_bad_json_duplicates_nonfinite_limits_and_unknown_fields(self):
        for body in (
            "{",
            '{"revision":1,"revision":2,"scene":{}}',
            '{"revision":NaN,"scene":{}}',
            "[" * 1000,
            '{"revision":1,"scene":{},"extra":1}',
        ):
            self.assertEqual(
                self.client.post(
                    self.url("save_scene"), body, content_type="application/json"
                ).status_code,
                400,
            )
        self.assertEqual(
            self.client.post(
                self.url("save_scene"), " " * 16001, content_type="application/json"
            ).status_code,
            413,
        )
        self.assertEqual(self.client.post(self.url("save_scene"), {}).status_code, 415)
        self.document.refresh_from_db()
        self.assertEqual(1, self.document.revision)

    def test_remote_asset_and_wrong_fixture_rejected(self):
        for field, value in (("fixture", "service"), ("schema_version", True)):
            scene = deepcopy(self.document.scene)
            scene[field] = value
            self.assertEqual(
                self.post({"revision": 1, "scene": scene}).status_code, 400
            )
        scene = deepcopy(self.document.scene)
        scene["layers"][0]["asset"] = "https://invalid.test/private"
        self.assertEqual(self.post({"revision": 1, "scene": scene}).status_code, 400)

    def test_foreign_owner_methods_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(
            client.post(
                self.url("save_scene"), "{}", content_type="application/json"
            ).status_code,
            403,
        )
        self.assertEqual(self.client.get(self.url("save_scene")).status_code, 405)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url("editor")).status_code, 404)
        self.assertEqual(
            self.post({"revision": 1, "scene": self.document.scene}).status_code, 404
        )
