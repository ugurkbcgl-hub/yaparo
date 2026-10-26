"""Closed metadata form: never accept candidate text or document ownership."""

from django import forms


class ApplyCopyForm(forms.Form):
    task_id = forms.UUIDField(widget=forms.HiddenInput)
    request_fingerprint = forms.RegexField(
        r"\A[0-9a-f]{64}\Z", widget=forms.HiddenInput
    )
    candidate_key = forms.RegexField(
        r"\A[a-z0-9][a-z0-9_-]{0,79}\Z", widget=forms.HiddenInput
    )
    candidate_digest = forms.RegexField(r"\A[0-9a-f]{64}\Z", widget=forms.HiddenInput)
    expected_revision = forms.IntegerField(
        min_value=1, max_value=2**31 - 1, widget=forms.HiddenInput
    )
    fields = forms.ChoiceField(
        choices=(("title", "Başlık"), ("title_subtitle", "Başlık ve açıklama")),
        widget=forms.HiddenInput,
    )
