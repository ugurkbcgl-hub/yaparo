"""Bounded fields for synthetic saved creative work; never accept scene JSON."""

import re

from django import forms
from django.core.exceptions import ValidationError

from growthtwin.modules.workspaces.brand_forms import PALETTE


def bounded_text(value):
    try:
        length = len(value.encode("utf-16-le")) // 2
    except UnicodeEncodeError:
        raise ValidationError("Geçerli bir örnek metin yazın.") from None
    if length > 100 or any(
        ord(character) < 32 and character != "\n" or ord(character) == 127
        for character in value
    ):
        raise ValidationError(
            "Metin en fazla 100 birim olmalı; özel kontrol karakterleri içeremez."
        )


class DocumentCreateForm(forms.Form):
    brand_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    expected_identity_version = forms.IntegerField(
        min_value=1, widget=forms.HiddenInput
    )
    request_id = forms.UUIDField(widget=forms.HiddenInput)
    palette_material_id = forms.UUIDField(required=False, widget=forms.HiddenInput)


class DocumentEditForm(forms.Form):
    expected_revision = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    title = forms.CharField(
        label="Başlık",
        required=False,
        strip=False,
        max_length=100,
        validators=[bounded_text],
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    title_color = forms.ChoiceField(label="Başlık rengi", choices=PALETTE)
    subtitle = forms.CharField(
        label="Alt başlık",
        required=False,
        strip=False,
        max_length=100,
        validators=[bounded_text],
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    subtitle_color = forms.ChoiceField(label="Alt başlık rengi", choices=PALETTE)

    def __init__(self, *args, scene, revision, **kwargs):
        layers = {layer["id"]: layer for layer in scene["layers"]}
        initial = {"expected_revision": revision}
        for name in ("title", "subtitle"):
            initial[name] = layers[name]["text"]
            initial[name + "_color"] = layers[name]["color"]
        super().__init__(*args, initial=initial, **kwargs)
        for name in ("title_color", "subtitle_color"):
            color = initial[name]
            if re.fullmatch(r"#[0-9a-fA-F]{6}", color) and color not in dict(PALETTE):
                self.fields[name].choices = (*PALETTE, (color, "Kayıtlı çalışma rengi"))
