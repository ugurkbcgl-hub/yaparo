"""Byte-level image rejection, normalization and metadata stripping evidence."""

from io import BytesIO

from django.test import SimpleTestCase
from PIL import Image, PngImagePlugin

from .raster_validation import MAX_SOURCE_BYTES, RasterRejected, normalize_raster


def image_bytes(format_name="PNG", *, size=(64, 48), **kwargs):
    with Image.new("RGB", size, "#254d9b") as image:
        output = BytesIO()
        image.save(output, format=format_name, **kwargs)
        return output.getvalue()


class RasterValidationTests(SimpleTestCase):
    def test_three_formats_decode_to_actual_metadata_free_png(self):
        for media, format_name in (
            ("image/jpeg", "JPEG"),
            ("image/png", "PNG"),
            ("image/webp", "WEBP"),
        ):
            with self.subTest(media=media):
                original = image_bytes(format_name)
                result = normalize_raster(original, declared_media_type=media)
                self.assertEqual(len(original), result.source_size)
                self.assertEqual((64, 48), (result.width, result.height))
                with Image.open(BytesIO(result.png)) as image:
                    image.load()
                    self.assertEqual("PNG", image.format)
                    self.assertEqual("RGBA", image.mode)
                    self.assertEqual({}, image.info)

    def test_metadata_is_removed_and_original_preserved(self):
        info = PngImagePlugin.PngInfo()
        info.add_text("comment", "untrusted fixture instructions")
        original = image_bytes(pnginfo=info)
        result = normalize_raster(original, declared_media_type="image/png")
        self.assertNotIn(b"untrusted fixture instructions", result.png)
        self.assertIn(b"untrusted fixture instructions", original)
        self.assertNotEqual(result.source_sha256, result.derivative_sha256)

    def test_invalid_truncated_wrong_type_and_oversized_bytes_fail_closed(self):
        valid = image_bytes()
        for source, media in (
            (b"", "image/png"),
            (b"<svg>script</svg>", "image/png"),
            (valid[:30], "image/png"),
            (valid, "image/jpeg"),
            (valid, "image/svg+xml"),
            (b"x" * (MAX_SOURCE_BYTES + 1), "image/png"),
            (bytearray(valid), "image/png"),
        ):
            with self.subTest(media=media, length=len(source)):
                with self.assertRaisesMessage(RasterRejected, "Raster input rejected."):
                    normalize_raster(source, declared_media_type=media)

    def test_dimensions_and_pixel_count_refused_before_decode(self):
        for size in ((4097, 1), (2001, 2000)):
            with self.subTest(size=size), self.assertRaises(RasterRejected):
                normalize_raster(
                    image_bytes(size=size), declared_media_type="image/png"
                )

    def test_animation_is_refused(self):
        with (
            Image.new("RGB", (8, 8), "red") as first,
            Image.new("RGB", (8, 8), "blue") as second,
        ):
            output = BytesIO()
            first.save(output, format="PNG", save_all=True, append_images=[second])
            with self.assertRaises(RasterRejected):
                normalize_raster(output.getvalue(), declared_media_type="image/png")

    def test_exif_orientation_is_applied_then_erased(self):
        exif = Image.Exif()
        exif[274] = 6
        result = normalize_raster(
            image_bytes("JPEG", exif=exif), declared_media_type="image/jpeg"
        )
        self.assertEqual((48, 64), (result.width, result.height))
        with Image.open(BytesIO(result.png)) as image:
            self.assertEqual(0, len(image.getexif()))
