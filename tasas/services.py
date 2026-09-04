from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from monedas.models import Moneda

from .models import ConsultaProveedorTasas, TasaReferencia
from .providers import ProveedorTasasError, ProveedorTasasHTTP


@dataclass(frozen=True)
class ResultadoConsultaTasas:
    """Resultado del caso de uso, incluyendo estado de frescura y error controlado."""

    estado: str
    tasas: list[TasaReferencia]
    mensaje: str | None = None


def _tasas_guardadas(moneda_base):
    return list(
        TasaReferencia.objects.filter(moneda_base=moneda_base)
        .select_related("moneda_base", "moneda_cotizada")
        .order_by("moneda_cotizada__codigo")
    )


def consultar_tasas_referencia(*, proveedor=None):
    """Actualiza las tasas externas o devuelve el último dato válido como fallback."""

    try:
        moneda_base = Moneda.objects.get(
            codigo=settings.TASAS_BASE_CURRENCY,
            estado="ACTIVA",
        )
    except Moneda.DoesNotExist:
        return ResultadoConsultaTasas(
            estado="indisponible",
            tasas=[],
            mensaje="La moneda base configurada no existe o está inactiva.",
        )

    cotizadas = list(Moneda.objects.activas().exclude(pk=moneda_base.pk))
    if not cotizadas:
        return ResultadoConsultaTasas(
            estado="vacio",
            tasas=[],
            mensaje="No hay monedas activas para consultar.",
        )

    proveedor = proveedor or ProveedorTasasHTTP()
    try:
        respuesta = proveedor.obtener(
            moneda_base.codigo,
            [moneda.codigo for moneda in cotizadas],
        )
    except ProveedorTasasError as exc:
        guardadas = _tasas_guardadas(moneda_base)
        return ResultadoConsultaTasas(
            estado="desactualizado" if guardadas else "indisponible",
            tasas=guardadas,
            mensaje=str(exc),
        )

    vigente_hasta = respuesta.fecha_hora + timedelta(
        seconds=settings.TASAS_VALIDITY_SECONDS
    )
    with transaction.atomic():
        consulta = ConsultaProveedorTasas.objects.create(
            fuente=respuesta.fuente,
            moneda_base=moneda_base,
            fecha_hora_fuente=respuesta.fecha_hora,
            respuesta=respuesta.respuesta_original,
        )
        for moneda in cotizadas:
            TasaReferencia.objects.update_or_create(
                moneda_base=moneda_base,
                moneda_cotizada=moneda,
                defaults={
                    "valor": respuesta.tasas[moneda.codigo],
                    "fuente": respuesta.fuente,
                    "fecha_hora_fuente": respuesta.fecha_hora,
                    "vigente_hasta": vigente_hasta,
                    "consulta": consulta,
                },
            )

    tasas = _tasas_guardadas(moneda_base)
    estado = "actualizado" if vigente_hasta >= timezone.now() else "desactualizado"
    return ResultadoConsultaTasas(estado=estado, tasas=tasas)
