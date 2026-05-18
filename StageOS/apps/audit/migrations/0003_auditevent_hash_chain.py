from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_auditevent_new_value_auditevent_old_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditevent',
            name='previous_hash',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='auditevent',
            name='record_hash',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
