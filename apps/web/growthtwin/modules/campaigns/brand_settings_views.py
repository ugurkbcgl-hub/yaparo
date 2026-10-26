"""Closed local plan form; validated history, no publish or budget instruction."""

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

from growthtwin.modules.workspaces.hosted_ad_views import _closed

from . import brand_ad_selection
from . import brand_settings as service


class PlanForm(forms.Form):
    goal = forms.ChoiceField(
        label="Kampanyanın amacı", choices=tuple(service.GOALS.items())
    )
    audience = forms.CharField(label="Hedef kitle (sentetik örnek)", max_length=200)
    region = forms.CharField(label="Planlanan bölge", max_length=100)
    budget = forms.DecimalField(
        label="Toplam medya bütçesi planı (TRY)",
        max_digits=9,
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=Decimal("9999999.99"),
        localize=True,
        widget=forms.TextInput(
            attrs={"inputmode": "decimal", "placeholder": "Örn. 2500,50"}
        ),
    )
    start = forms.DateField(
        label="Başlangıç tarihi",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    end = forms.DateField(
        label="Bitiş tarihi",
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    synthetic_confirmation = forms.BooleanField(
        label="Yalnız sentetik plan kaydediyorum; ödeme, reklam yayını veya harcama izni vermiyorum."
    )
    expected_version = forms.IntegerField(
        min_value=0, max_value=2**31 - 2, widget=forms.HiddenInput
    )
    request_id = forms.UUIDField(widget=forms.HiddenInput)

    def values(self):
        data = self.cleaned_data
        return {
            "goal": data["goal"],
            "audience": data["audience"],
            "region": data["region"],
            "budget_minor": int(data["budget"] * 100),
            "start": data["start"].isoformat(),
            "end": data["end"].isoformat(),
        }


@login_required
@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@csrf_protect
@sensitive_post_parameters("audience", "region", "budget")
def setup(request, draft_id):
    try:
        service.enabled()
        plan = brand_ad_selection.campaign(request.user, draft_id)
        current = service.read(owner=request.user, campaign_id=plan.pk)
    except (PermissionDenied, ObjectDoesNotExist) as error:
        raise Http404 from error
    except Exception:
        return HttpResponse(
            "Kaydedilmiş plan doğrulanamadı. Mevcut kayıt korunuyor.", status=409
        )
    initial = {
        "goal": "awareness",
        "start": service.today(),
        "end": service.today() + timedelta(days=6),
        "expected_version": current.version if current else 0,
        "request_id": uuid4(),
    }
    if current:
        values = current.payload["settings"]
        initial.update(
            {
                **values,
                "budget": (Decimal(values["budget_minor"]) / 100).quantize(
                    Decimal("0.01")
                ),
            }
        )
    form = PlanForm(request.POST if request.method == "POST" else None, initial=initial)
    status = 200
    if request.method == "POST":
        if _closed(request.POST, form.fields) and form.is_valid():
            try:
                service.save(
                    owner=request.user,
                    campaign_id=plan.pk,
                    expected_version=form.cleaned_data["expected_version"],
                    request_id=form.cleaned_data["request_id"],
                    values=form.values(),
                )
            except (PermissionDenied, ObjectDoesNotExist) as error:
                raise Http404 from error
            except ValidationError as error:
                form.add_error(None, error)
            except Exception:
                form.add_error(
                    None,
                    "Plan kaydedilemedi. Mevcut kayıt korunuyor; güncel planı açın.",
                )
            else:
                return redirect("campaigns:brand_ad_choose", draft_id=plan.pk)
        status = 409
    return render(
        request,
        "campaigns/brand_settings.html",
        {
            "plan": plan,
            "form": form,
            "saved_plan": service.summary(current),
            "failed_save": status == 409,
        },
        status=status,
    )
