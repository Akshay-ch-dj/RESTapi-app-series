# Generated by Django 2.2.14 on 2020-07-20 16:15

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_series'),
    ]

    operations = [
        migrations.AddField(
            model_name='series',
            name='Image',
            field=models.ImageField(null=True, upload_to=core.models.series_image_file_path),
        ),
    ]