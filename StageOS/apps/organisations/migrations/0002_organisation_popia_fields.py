import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0001_initial'),
        ('accounts', '0002_alter_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='information_officer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='information_officer_for',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='organisation',
            name='popia_privacy_notice_url',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organisation',
            name='default_retention_days',
            field=models.PositiveIntegerField(default=365),
        ),
    ]
