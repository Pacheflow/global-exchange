from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from monedas.models import Moneda


class ConsultaProveedorTasas(models.Model):
    """Última respuesta externa válida conservada para trazabilidad y fallback."""

    fuente = models.CharField(max_length=100)
    moneda_base = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        related_name="consultas_tasas",
    )
    fecha_hora_fuente = models.DateTimeField()
    recibida_en = models.DateTimeField(auto_now_add=True)
    respuesta = models.JSONField()

    class Meta:
        ordering = ("-recibida_en",)
        verbose_name = "consulta válida al proveedor de tasas"
        verbose_name_plural = "consultas válidas al proveedor de tasas"

    def __str__(self):
        return f"{self.fuente} · {self.moneda_base.codigo} · {self.fecha_hora_fuente}"


class TasaReferencia(models.Model):
    """Última tasa externa válida normalizada para un par de monedas."""

    moneda_base = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        related_name="tasas_referencia_base",
    )
    moneda_cotizada = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        related_name="tasas_referencia_cotizada",
    )
    valor = models.DecimalField(
        max_digits=24,
        decimal_places=10,
        validators=[MinValueValidator(Decimal("0.0000000001"))],
    )
    fuente = models.CharField(max_length=100)
    fecha_hora_fuente = models.DateTimeField()
    vigente_hasta = models.DateTimeField()
    actualizada_en = models.DateTimeField(auto_now=True)
    consulta = models.ForeignKey(
        ConsultaProveedorTasas,
        on_delete=models.PROTECT,
        related_name="tasas",
    )

    class Meta:
        ordering = ("moneda_base__codigo", "moneda_cotizada__codigo")
        constraints = [
            models.UniqueConstraint(
                fields=("moneda_base", "moneda_cotizada"),
                name="tasa_referencia_par_unico",
            ),
            models.CheckConstraint(
                condition=~models.Q(moneda_base=models.F("moneda_cotizada")),
                name="tasa_referencia_monedas_distintas",
            ),
            models.CheckConstraint(
                condition=models.Q(valor__gt=0),
                name="tasa_referencia_valor_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.moneda_base.codigo}/{self.moneda_cotizada.codigo}: {self.valor}"
