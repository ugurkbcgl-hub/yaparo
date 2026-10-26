"""Bounded image transport tests, no network or real credential."""

import base64
import json
from unittest import mock

from django.test import SimpleTestCase

from . import openrouter_image as transport


class ImageTransportTests(SimpleTestCase):
    @mock.patch.object(transport, "HTTPSConnection")
    def test_privacy_request_one_output_valid_cost_and_large_envelope(self, connection):
        data = transport.PNG_SIGNATURE + b"a" * 70_000
        payload = {
            "data": [
                {"b64_json": base64.b64encode(data).decode(), "media_type": "image/png"}
            ],
            "usage": {"cost": 0.033625},
        }
        connection.return_value.getresponse.return_value = mock.Mock(
            status=200, read=mock.Mock(return_value=json.dumps(payload).encode())
        )
        output = transport.generate_image("test-key", prompt="fixed fictional prompt")
        self.assertEqual(output, (data, ".png", 0.033625))
        request = connection.return_value.request
        request.assert_called_once()
        body = json.loads(request.call_args.kwargs["body"])
        self.assertEqual(body["provider"]["only"], [transport.PROVIDER])
        self.assertFalse(body["provider"]["allow_fallbacks"])
        self.assertTrue(body["provider"]["zdr"])
        self.assertEqual(body["provider"]["data_collection"], "deny")
        self.assertEqual(body["n"], 1)

    @mock.patch.object(transport, "HTTPSConnection")
    def test_duplicate_cost_nonfinite_and_malformed_media_refuse(self, connection):
        encoded = base64.b64encode(transport.PNG_SIGNATURE).decode()
        for body in (
            '{"data":[],"usage":{"cost":0.03,"cost":0.001}}',
            '{"data":[],"usage":{"cost":NaN}}',
            json.dumps(
                {
                    "data": [{"b64_json": encoded, "media_type": "image/jpeg"}],
                    "usage": {"cost": 0.03},
                }
            ),
            json.dumps({"data": [{"b64_json": encoded}], "usage": {"cost": True}}),
        ):
            with self.subTest(body=body):
                connection.reset_mock()
                connection.return_value.getresponse.return_value = mock.Mock(
                    status=200, read=mock.Mock(return_value=body.encode())
                )
                with self.assertRaises(transport.ImageEvaluationFailure):
                    transport.generate_image("test-key")
                connection.return_value.request.assert_called_once()

    @mock.patch.object(transport, "HTTPSConnection")
    def test_bad_key_refuses_before_network(self, connection):
        with self.assertRaises(transport.ImageEvaluationFailure):
            transport.generate_image("invalid\nkey")
        connection.assert_not_called()
