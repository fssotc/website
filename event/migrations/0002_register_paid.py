# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-11 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
