# Generated by Django 3.1.7 on 2021-03-15 17:08

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20210315_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
