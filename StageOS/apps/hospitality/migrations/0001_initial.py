import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_alter_user_user_type'),
        ('contexts', '0001_initial'),
        ('organisations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HospitalityRequest',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'request_type',
                    models.CharField(
                        choices=[
                            ('vip_hosting', 'VIP Hosting'),
                            ('catering', 'Catering'),
                            ('private_dining', 'Private Dining'),
                            ('restaurant_reservation', 'Restaurant Reservation'),
                            ('other', 'Other'),
                        ],
                        max_length=30,
                    ),
                ),
                ('event_date', models.DateField()),
                ('guest_count', models.PositiveIntegerField(default=1)),
                ('special_requirements', models.TextField(blank=True)),
                ('dietary_restrictions', models.TextField(blank=True)),
                ('contact_name', models.CharField(max_length=255)),
                ('contact_phone', models.CharField(blank=True, max_length=30)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('draft', 'Draft'),
                            ('submitted', 'Submitted'),
                            ('confirmed', 'Confirmed'),
                            ('declined', 'Declined'),
                            ('completed', 'Completed'),
                        ],
                        default='draft',
                        max_length=20,
                    ),
                ),
                ('notes_text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'organisation',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='organisations.organisation',
                    ),
                ),
                (
                    'operating_context',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='hospitality_requests',
                        to='contexts.operatingcontext',
                    ),
                ),
                (
                    'assigned_to',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='hospitality_assignments',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='created_hospitality_requests',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-event_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HospitalityNote',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('note_text', models.TextField()),
                (
                    'note_type',
                    models.CharField(
                        choices=[
                            ('internal', 'Internal'),
                            ('client_facing', 'Client Facing'),
                        ],
                        default='internal',
                        max_length=20,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'organisation',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='organisations.organisation',
                    ),
                ),
                (
                    'hospitality_request',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notes',
                        to='hospitality.hospitalityrequest',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='hospitality_notes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
