# Generated by Django 5.1.2 on 2024-10-19 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='english_keywords',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='spanish_keywords',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
