import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_popia_consent'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='invite_token',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
    ]
