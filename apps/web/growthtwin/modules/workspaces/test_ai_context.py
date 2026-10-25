"""Offline task bindings reject stale/foreign context without provider access."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase, override_settings

from growthtwin.modules.ai_gateway.brand_tasks import (
    ADAPTER_ID,
    BrandCopyTaskResult,
    validate_request,
    validate_result,
)
from growthtwin.modules.ai_gateway.contracts import CreativeGenerationRejected
from growthtwin.modules.ai_gateway.synthetic import SyntheticTemplateGenerator
from growthtwin.modules.campaigns.test_design_selection import SelectionFixture

from .ai_context import build_selected_brand_task, validate_selected_brand_result
from .models import Brand, Workspace


@override_settings(DEBUG=True, SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=True)
class BrandTaskContractTests(SelectionFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.select()
        self.task_id = uuid4()
        self.request = self.build()

    def build(self, **changes):
        return build_selected_brand_task(
            **(
                dict(
                    owner=self.owner,
                    draft_id=self.draft.pk,
                    selection_version=1,
                    task_id=self.task_id,
                )
                | changes
            )
        )

    def result(self, **changes):
        return BrandCopyTaskResult(
            **(
                dict(
                    task_id=self.task_id,
                    request_fingerprint=self.request.fingerprint,
                    adapter_id=ADAPTER_ID,
                    status="candidate",
                    creative_result=SyntheticTemplateGenerator().generate(
                        self.request.creative_request
                    ),
                )
                | changes
            )
        )

    def accept(self, result):
        return validate_selected_brand_result(
            owner=self.owner,
            draft_id=self.draft.pk,
            request=self.request,
            result=result,
        )

    def test_immutable_reproducible_brand_scene_sources_and_real_identity_input(self):
        self.assertEqual(self.request, self.build())
        self.assertEqual(self.request.fingerprint, self.build().fingerprint)
        self.assertNotEqual(
            self.request.fingerprint, self.build(task_id=uuid4()).fingerprint
        )
        self.assertEqual(self.request.context.brand_id, self.brand.pk)
        self.assertEqual(self.request.context.document_revision, 1)
        self.assertEqual(
            self.request.identity.primary_color, self.document.identity.primary_color
        )
        self.assertEqual(self.request.identity.tone, self.document.identity.tone)
        self.assertEqual(
            tuple(s.layer_id for s in self.request.context.materials), ("hero", "logo")
        )
        self.assertEqual(
            self.request.creative_request.brief.brand_context, self.brand.name
        )
        self.assertNotIn(
            self.draft.brand_name, self.request.creative_request.brief.text
        )
        with self.assertRaises(FrozenInstanceError):
            self.request.context.brand_id = 99
        self.assertFalse(self.request.execution_authorized)
        result = self.accept(self.result())
        self.assertTrue(result.review_required)
        self.assertFalse(result.publishable)

    def test_live_document_edit_preserves_selected_task_but_reselection_refuses(self):
        result = self.result()
        scene = deepcopy(self.document.scene)
        scene["layers"][2]["text"] = "Sonraki tasarım kaydı"
        self.save(scene)
        self.assertEqual(self.build().fingerprint, self.request.fingerprint)
        self.assertEqual(self.accept(result), result)
        self.select(
            expected_document_revision=2,
            expected_selection_version=1,
            request_id=uuid4(),
        )
        with self.assertRaises(ValidationError):
            self.accept(result)

    def test_owner_scope_revocation_and_flags(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.build(owner=self.other)
        with self.settings(SYNTHETIC_CAMPAIGN_DESIGN_ENABLED=False):
            from django.core.exceptions import PermissionDenied

            with self.assertRaises(PermissionDenied):
                self.build()
        Workspace.objects.filter(pk=self.workspace.pk).update(owner=self.other)
        with self.assertRaises(ObjectDoesNotExist):
            self.accept(self.result())

    def test_archived_source_and_other_owned_workspace_refuse(self):
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        with self.assertRaises(ObjectDoesNotExist):
            self.build()
        other = Workspace.objects.create(owner=self.owner, name="Other owned workspace")
        Brand.objects.filter(pk=self.brand.pk).update(
            is_archived=False, workspace=other
        )
        with self.assertRaises(ObjectDoesNotExist):
            self.build()

    def test_unsupported_schema_cost_adapter_identity_and_source_shapes_refuse(self):
        bad_contexts = (
            replace(self.request.context, brand_id=True),
            replace(self.request.context, scene_digest="bad"),
            replace(
                self.request.context, materials=list(self.request.context.materials)
            ),
        )
        bad_requests = [
            replace(self.request, context=context) for context in bad_contexts
        ]
        bad_requests += [
            replace(self.request, schema_version=True),
            replace(self.request, schema_version=2),
            replace(self.request, max_cost_microusd=1),
            replace(self.request, reservation_id=uuid4()),
            replace(self.request, allowed_adapters=("unapproved-provider",)),
            replace(
                self.request, identity=replace(self.request.identity, tone="formal")
            ),
            replace(
                self.request,
                creative_request=replace(
                    self.request.creative_request, synthetic_only=False
                ),
            ),
        ]
        for request in bad_requests:
            with self.subTest(request_type=type(request).__name__):
                with self.assertRaises(CreativeGenerationRejected):
                    validate_request(request)

    def test_response_request_task_adapter_cost_shape_and_context_mismatch_refuse(self):
        result = self.result()
        bad_results = (
            replace(result, schema_version=2),
            replace(result, task_id=uuid4()),
            replace(result, request_fingerprint="0" * 64),
            replace(result, adapter_id="other"),
            replace(result, status="published"),
            replace(result, reported_cost_microusd=1),
            replace(
                result,
                creative_result=replace(result.creative_result, generator_id="other"),
            ),
            replace(result, status="failed"),
        )
        for bad in bad_results:
            with self.assertRaises(CreativeGenerationRejected):
                self.accept(bad)
        with self.assertRaises(CreativeGenerationRejected):
            validate_result(
                self.request,
                result,
                current_context=replace(self.request.context, selection_version=2),
            )
        for state in ("failed", "uncertain"):
            accepted = self.accept(self.result(status=state, creative_result=None))
            self.assertFalse(accepted.publishable)

    def test_forged_dataclass_binding_is_not_owned_authority(self):
        request = replace(
            self.request,
            context=replace(self.request.context, brand_id=self.service.pk),
        )
        result = replace(self.result(), request_fingerprint=request.fingerprint)
        with self.assertRaises(CreativeGenerationRejected):
            validate_selected_brand_result(
                owner=self.owner, draft_id=self.draft.pk, request=request, result=result
            )

    def test_same_source_other_campaign_cannot_accept_result(self):
        second = self.draft.__class__.objects.get(pk=self.draft.pk)
        second.pk = None
        second.save()
        from growthtwin.modules.campaigns.design_selection import select_design

        select_design(
            owner=self.owner,
            draft_id=second.pk,
            brand_id=self.brand.pk,
            document_id=self.document.pk,
            expected_document_revision=1,
            expected_selection_version=0,
            request_id=uuid4(),
        )
        with self.assertRaises(CreativeGenerationRejected):
            validate_selected_brand_result(
                owner=self.owner,
                draft_id=second.pk,
                request=self.request,
                result=self.result(),
            )

    def test_rehashed_foreign_brief_is_not_fixed_factory_authority(self):
        brief = replace(
            self.request.creative_request.brief, text="Untrusted caller replacement"
        )
        request = replace(
            self.request,
            creative_request=replace(self.request.creative_request, brief=brief),
        )
        result = BrandCopyTaskResult(
            task_id=self.task_id,
            request_fingerprint=request.fingerprint,
            adapter_id=ADAPTER_ID,
            status="candidate",
            creative_result=SyntheticTemplateGenerator().generate(
                request.creative_request
            ),
        )
        with self.assertRaises(CreativeGenerationRejected):
            validate_selected_brand_result(
                owner=self.owner, draft_id=self.draft.pk, request=request, result=result
            )
