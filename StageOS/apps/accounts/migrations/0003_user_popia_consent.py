from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='data_processing_consent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='data_processing_consent_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
