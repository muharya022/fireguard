# Generated by Django 5.2.1 on 2025-06-03 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0002_remove_detectionhistory_image_detectionhistory_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detectionhistory',
            name='filepath',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
