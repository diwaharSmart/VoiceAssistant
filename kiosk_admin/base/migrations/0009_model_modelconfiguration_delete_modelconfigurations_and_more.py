# Generated by Django 5.1.2 on 2024-10-26 05:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_configuration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('system_instruction', models.TextField(blank=True, null=True)),
                ('temperature', models.CharField(blank=True, max_length=255, null=True)),
                ('top_p', models.CharField(blank=True, max_length=255, null=True)),
                ('top_k', models.CharField(blank=True, max_length=255, null=True)),
                ('max_output_tokens', models.CharField(blank=True, max_length=255, null=True)),
                ('response_mime_type', models.CharField(blank=True, max_length=255, null=True)),
                ('welcome_text', models.TextField(blank=True, null=True)),
                ('post_welcome_text', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModelConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=255, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.model')),
            ],
        ),
        migrations.DeleteModel(
            name='ModelConfigurations',
        ),
        migrations.AlterField(
            model_name='configuration',
            name='key',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
