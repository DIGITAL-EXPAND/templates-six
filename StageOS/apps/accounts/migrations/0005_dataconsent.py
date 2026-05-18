import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_invite_token'),
        ('documents', '0004_alter_document_file_size'),
        ('organisations', '0002_organisation_popia_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataConsent',
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
                    'organisation',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='organisations.organisation',
                    ),
                ),
                (
                    'subject_type',
                    models.CharField(
                        choices=[
                            ('user', 'User'),
                            ('supplier', 'Supplier'),
                            ('artist', 'Artist'),
                            ('client', 'Client'),
                            ('youth_learner', 'Youth Learner'),
                        ],
                        max_length=20,
                    ),
                ),
                ('subject_id', models.UUIDField()),
                (
                    'lawful_basis',
                    models.CharField(
                        choices=[
                            ('consent', 'Consent'),
                            ('legitimate_interest', 'Legitimate Interest'),
                            ('legal_obligation', 'Legal Obligation'),
                            ('vital_interest', 'Vital Interest'),
                            ('public_task', 'Public Task'),
                        ],
                        max_length=30,
                    ),
                ),
                ('purpose', models.TextField()),
                ('consent_given', models.BooleanField(default=False)),
                ('consent_date', models.DateTimeField(blank=True, null=True)),
                (
                    'consent_document',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='consent_records',
                        to='documents.document',
                    ),
                ),
                ('withdrawal_date', models.DateTimeField(blank=True, null=True)),
                ('retention_until', models.DateField(blank=True, null=True)),
                (
                    'recorded_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='recorded_consents',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
