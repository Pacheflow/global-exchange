# HU-17 — Consultar y visualizar tasas

**Responsable backend:** Guillermo  
**Sprint:** 2 — Hito 4

## Objetivo

Obtener tasas de referencia desde un proveedor externo, validarlas, persistir la última respuesta válida y ofrecer un contrato de consulta que distinga expresamente datos actualizados, datos de respaldo desactualizados e indisponibilidad.

## Flujo técnico

```text
GET /tasas/
  -> autenticación OIDC
  -> servicio consultar_tasas_referencia
  -> catálogo de monedas activas (HU-36)
  -> adaptador ProveedorTasasHTTP
  -> validación y normalización
  -> transacción PostgreSQL
       -> ConsultaProveedorTasas (respuesta válida)
       -> TasaReferencia (último valor por par)
  -> respuesta JSON
```

Si el proveedor falla, el servicio no guarda la respuesta fallida:

```text
Fallo externo
  |-- existe TasaReferencia -> HTTP 200, estado desactualizado
  `-- no existe dato previo -> HTTP 503, estado indisponible
```

## Modelos

### `ConsultaProveedorTasas`

Conserva cada respuesta externa válida para trazabilidad:

- Fuente.
- Moneda base.
- Fecha/hora informada por el proveedor.
- Fecha/hora de recepción.
- Respuesta JSON original.

### `TasaReferencia`

Mantiene el último dato válido normalizado por par:

- Moneda base y moneda cotizada.
- Valor decimal positivo.
- Fuente.
- Fecha/hora del proveedor.
- Vigencia calculada.
- Consulta de origen.

La base de datos impide pares repetidos, monedas iguales en un par y valores menores o iguales a cero.

## Configuración

| Variable | Valor predeterminado | Descripción |
|---|---|---|
| `TASAS_PROVIDER_URL` | `https://open.er-api.com/v6/latest/__BASE__` | URL; debe admitir el marcador `__BASE__`. |
| `TASAS_PROVIDER_API_KEY` | vacío | Credencial opcional enviada como Bearer token. |
| `TASAS_PROVIDER_TIMEOUT` | `5` | Timeout HTTP en segundos. |
| `TASAS_PROVIDER_NAME` | `ExchangeRate-API` | Fuente visible y persistida. |
| `TASAS_BASE_CURRENCY` | `USD` | Código de moneda base activa. |
| `TASAS_VALIDITY_SECONDS` | `86400` | Duración de la vigencia desde la fecha externa. |

No se deben versionar credenciales reales. Deben declararse en `.env`.

## Contrato de consulta

### Solicitud

```http
GET /tasas/
Cookie: sessionid=...
```

La ruta requiere una sesión OIDC válida.

### Respuesta actualizada — HTTP 200

```json
{
  "estado": "actualizado",
  "mensaje": null,
  "tasas_referencia": [
    {
      "id": 1,
      "tipo": "REFERENCIA",
      "par": "USD/EUR",
      "moneda_base": "USD",
      "moneda_cotizada": "EUR",
      "valor": "0.8600000000",
      "fuente": "ExchangeRate-API",
      "fecha_hora": "2026-09-04T12:00:00+00:00",
      "vigente_hasta": "2026-09-05T12:00:00+00:00",
      "desactualizada": false
    }
  ],
  "tasas_comerciales": []
}
```

### Fallback — HTTP 200

Devuelve el mismo formato con:

```json
{
  "estado": "desactualizado",
  "mensaje": "El proveedor excedió el tiempo de espera.",
  "tasas_referencia": [{"desactualizada": true}],
  "tasas_comerciales": []
}
```

### Sin datos previos — HTTP 503

```json
{
  "estado": "indisponible",
  "mensaje": "No fue posible consultar el proveedor de tasas.",
  "tasas_referencia": [],
  "tasas_comerciales": []
}
```

### Otros estados

- `401`: no existe una sesión válida.
- `vacio`: la moneda base existe, pero no hay monedas cotizadas activas.
- `indisponible`: la moneda base configurada no existe o está inactiva.

## Separación respecto de HU-21

HU-17 administra exclusivamente referencias externas. El contrato reserva `tasas_comerciales` como colección independiente, inicialmente vacía. HU-21 deberá poblarla desde su propio modelo/servicio sin modificar ni permitir edición manual de `TasaReferencia`.

## Errores controlados

El adaptador rechaza:

- Timeout.
- Error de red.
- Estado HTTP inválido.
- JSON inválido.
- Estructura incompleta.
- Moneda base diferente.
- Monedas solicitadas ausentes.
- Valores no numéricos, infinitos, cero o negativos.
- Fecha/hora inválida.

Solo una respuesta completamente válida entra en la transacción de persistencia.

## Pruebas

```powershell
docker compose exec web python manage.py test tasas
```

Las pruebas usan mocks y no dependen de Internet. Cubren normalización, éxito, timeout, HTTP inválido, JSON inválido/incompleto, valores inválidos, persistencia, actualización, fallback, ausencia de datos, moneda base inactiva, catálogo vacío, autenticación y respuesta del endpoint.

## Migración

```powershell
docker compose exec web python manage.py migrate
```

La migración incorporada es `tasas/migrations/0001_initial.py`.
