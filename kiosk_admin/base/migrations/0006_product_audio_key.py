# Generated by Django 5.1.2 on 2024-10-22 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_modelconfigurations'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='audio_key',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
