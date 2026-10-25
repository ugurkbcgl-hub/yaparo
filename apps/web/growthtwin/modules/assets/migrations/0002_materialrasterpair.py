import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("assets", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="MaterialRasterPair",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("original", models.BinaryField()),
                ("derivative", models.BinaryField()),
                ("original_sha256", models.CharField(max_length=64)),
                ("derivative_sha256", models.CharField(max_length=64)),
                ("original_size", models.PositiveIntegerField()),
                ("derivative_size", models.PositiveIntegerField()),
                ("tool", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "version",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="raster",
                        to="assets.brandmaterialversion",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            original_size__gte=1, original_size__lte=3145728
                        ),
                        name="material_raster_original_size_bound",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            derivative_size__gte=1, derivative_size__lte=8388608
                        ),
                        name="material_raster_derivative_size_bound",
                    ),
                ]
            },
        ),
    ]
