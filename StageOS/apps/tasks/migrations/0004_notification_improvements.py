from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_taskcomment_evidence_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='related_model',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='related_id',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
    ]
