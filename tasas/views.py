from django.http import JsonResponse
from django.views.decorators.http import require_GET

from usuarios.decorators import requiere_autenticacion

from .services import consultar_tasas_referencia


def _serializar_tasa(tasa, *, desactualizada):
    return {
        "id": tasa.id,
        "tipo": "REFERENCIA",
        "par": f"{tasa.moneda_base.codigo}/{tasa.moneda_cotizada.codigo}",
        "moneda_base": tasa.moneda_base.codigo,
        "moneda_cotizada": tasa.moneda_cotizada.codigo,
        "valor": str(tasa.valor),
        "fuente": tasa.fuente,
        "fecha_hora": tasa.fecha_hora_fuente.isoformat(),
        "vigente_hasta": tasa.vigente_hasta.isoformat(),
        "desactualizada": desactualizada,
    }


@requiere_autenticacion
@require_GET
def consultar_tasas(request):
    """Consulta tasas reales y comunica expresamente frescura o indisponibilidad."""

    resultado = consultar_tasas_referencia()
    desactualizada = resultado.estado == "desactualizado"
    payload = {
        "estado": resultado.estado,
        "mensaje": resultado.mensaje,
        "tasas_referencia": [
            _serializar_tasa(tasa, desactualizada=desactualizada)
            for tasa in resultado.tasas
        ],
        # Contrato reservado para HU-21. Nunca se mezcla una tasa comercial
        # con la referencia externa ni se fabrica información inexistente.
        "tasas_comerciales": [],
    }
    return JsonResponse(
        payload,
        status=503 if resultado.estado == "indisponible" else 200,
    )
