from django.db import models
from django.utils.translation import gettext_lazy as _

from core.db.models import DBModel


class Currency(DBModel):
    name = models.CharField(_("Name"), max_length=10, unique=True)

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return self.name


class Provider(DBModel):
    name = models.CharField(
        _("Name"), max_length=50, unique=True, editable=False, null=False
    )
    api_key = models.CharField(
        _("API key"), max_length=255, null=True, blank=True, default=None
    )

    class Meta:
        verbose_name = _("Provider")
        verbose_name_plural = _("Providers")

    def __str__(self):
        return self.name


class Block(DBModel):
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="blocks"
    )
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="blocks"
    )
    block_number = models.BigIntegerField(_("Block number"))
    created_at = models.DateTimeField(_("Created at"), null=False, blank=True)
    stored_at = models.DateTimeField(_("Stored at"), auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Block")
        verbose_name_plural = _("Blocks")
        unique_together = (
            "currency",
            "block_number",
        )

    def __str__(self):
        return f"{self.currency.name} - Block {self.block_number}"
