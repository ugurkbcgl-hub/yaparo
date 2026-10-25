"""Private records for Yaparo's fixed synthetic material kit.

Catalog rows record source/version metadata; a separate immutable raster pair
holds only generated palette-image bytes. No uploaded bytes, storage paths,
public URLs or AI permission are accepted. Customer intake remains closed.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models


class BrandMaterialQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError(
            "Materyal kayıtları uygulama hizmeti dışında değiştirilemez."
        )

    def bulk_update(self, objs, fields, **kwargs):
        raise ValidationError(
            "Materyal kayıtları uygulama hizmeti dışında değiştirilemez."
        )


class BrandMaterial(models.Model):
    """One owner-scoped catalog item, permanently tied to a brand identity."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        "workspaces.Brand", on_delete=models.CASCADE, related_name="materials"
    )
    identity = models.ForeignKey(
        "workspaces.BrandIdentity",
        on_delete=models.PROTECT,
        related_name="materials",
    )
    source_key = models.CharField(max_length=64)
    current_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BrandMaterialQuerySet.as_manager()

    class Meta:
        ordering = ("source_key", "pk")
        constraints = [
            models.UniqueConstraint(
                fields=("brand", "source_key"),
                name="brand_material_source_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(current_version__gte=1),
                name="brand_material_current_version_positive",
            ),
        ]

    def clean(self):
        super().clean()
        if (
            self.brand_id
            and self.identity_id
            and self.identity.brand_id != self.brand_id
        ):
            raise ValidationError("Materyal kimliği aynı markaya ait olmalıdır.")
        if self.brand_id:
            from .synthetic_catalog import definitions_for_fixture

            allowed = {
                item.source_key for item in definitions_for_fixture(self.brand.fixture)
            }
            allowed.add(f"{self.brand.fixture}:palette:v1")
            if self.source_key not in allowed:
                raise ValidationError({"source_key": "Bilinmeyen sentetik kaynak."})

    def save(self, *args, **kwargs):
        original = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        if original:
            raise ValidationError(
                "Materyal kayıtları uygulama hizmeti dışında değiştirilemez."
            )
        self.full_clean()
        return super().save(*args, **kwargs)


class BrandMaterialVersionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Materyal sürümleri değiştirilemez.")

    def delete(self):
        raise ValidationError("Materyal sürümleri tek başına silinemez.")

    def bulk_update(self, objs, fields, **kwargs):
        raise ValidationError("Materyal sürümleri değiştirilemez.")


class BrandMaterialVersion(models.Model):
    """Immutable catalog metadata, not an uploaded file or a security verdict."""

    material = models.ForeignKey(
        BrandMaterial, on_delete=models.CASCADE, related_name="versions"
    )
    version = models.PositiveIntegerField()
    display_name = models.CharField(max_length=120)
    media_type = models.CharField(max_length=32)
    byte_size = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    source_label = models.CharField(max_length=120)
    rights_label = models.CharField(max_length=120)
    catalog_digest = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BrandMaterialVersionQuerySet.as_manager()

    class Meta:
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(
                fields=("material", "version"),
                name="brand_material_version_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="brand_material_version_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(byte_size__gte=1),
                name="brand_material_byte_size_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(width__gte=1), name="brand_material_width_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(height__gte=1),
                name="brand_material_height_positive",
            ),
        ]

    def clean(self):
        super().clean()
        from .synthetic_catalog import (
            ALLOWED_MEDIA_TYPES,
            MAX_BYTES,
            MAX_HEIGHT,
            MAX_WIDTH,
        )

        if self.media_type not in ALLOWED_MEDIA_TYPES:
            raise ValidationError({"media_type": "Desteklenmeyen materyal türü."})
        if self.byte_size is not None and self.byte_size > MAX_BYTES:
            raise ValidationError({"byte_size": "Materyal boyut sınırı aşıldı."})
        if self.width > MAX_WIDTH or self.height > MAX_HEIGHT:
            raise ValidationError("Materyal piksel sınırı aşıldı.")
        if len(self.catalog_digest) != 64 or any(
            char not in "0123456789abcdef" for char in self.catalog_digest.lower()
        ):
            raise ValidationError({"catalog_digest": "Geçerli katalog özeti gerekli."})

    def save(self, *args, **kwargs):
        if not self._state.adding or self.pk is not None:
            raise ValidationError("Materyal sürümleri değiştirilemez.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Materyal sürümleri tek başına silinemez.")


class MaterialRasterPair(models.Model):
    """Immutable, bounded synthetic original/derivative stored atomically in DB.

    This prototype adapter uses the existing database rather than a filesystem
    path or public media bucket. Its bytes remain behind owner-scoped services.
    """

    version = models.OneToOneField(
        BrandMaterialVersion, on_delete=models.CASCADE, related_name="raster"
    )
    original = models.BinaryField()
    derivative = models.BinaryField()
    original_sha256 = models.CharField(max_length=64)
    derivative_sha256 = models.CharField(max_length=64)
    original_size = models.PositiveIntegerField()
    derivative_size = models.PositiveIntegerField()
    tool = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = BrandMaterialVersionQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(original_size__gte=1, original_size__lte=3145728),
                name="material_raster_original_size_bound",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    derivative_size__gte=1, derivative_size__lte=8388608
                ),
                name="material_raster_derivative_size_bound",
            ),
        ]

    def clean(self):
        super().clean()
        from hashlib import sha256

        for field, size, digest in (
            (self.original, self.original_size, self.original_sha256),
            (self.derivative, self.derivative_size, self.derivative_sha256),
        ):
            if len(field) != size or sha256(field).hexdigest() != digest:
                raise ValidationError("Raster bytes do not match their metadata.")

    def save(self, *args, **kwargs):
        if not self._state.adding or self.pk is not None:
            raise ValidationError("Raster pairs are immutable.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Raster pairs cannot be deleted independently.")
