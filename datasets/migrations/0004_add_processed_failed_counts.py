# Generated migration for processed_count and failed_count fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0003_dataset_error_message_dataset_processed_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='processed_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dataset',
            name='failed_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
