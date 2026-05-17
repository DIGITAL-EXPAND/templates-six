from django.db import models


class TenantOwnedModel(models.Model):
    """Abstract base for all tenant-scoped business records.

    Every concrete subclass is automatically scoped to an Organisation.
    All querysets must filter by organisation — enforced in views via
    TenantQuerysetMixin.
    """
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.PROTECT,
        related_name='+',
    )

    class Meta:
        abstract = True
