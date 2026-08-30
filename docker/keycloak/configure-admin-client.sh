#!/bin/sh
set -eu

KCADM=/opt/keycloak/bin/kcadm.sh
SERVER_URL=${KEYCLOAK_INTERNAL_URL:-http://keycloak:8080}
REALM=${KEYCLOAK_REALM:-global-exchange}
CLIENT_ID=${KEYCLOAK_ADMIN_CLIENT_ID:-global-exchange-admin-api}
CLIENT_SECRET=${KEYCLOAK_ADMIN_CLIENT_SECRET:?KEYCLOAK_ADMIN_CLIENT_SECRET es obligatorio}

echo "Configurando cliente técnico de administración de Keycloak..."
"$KCADM" config credentials \
  --server "$SERVER_URL" \
  --realm master \
  --user "$KEYCLOAK_ADMIN" \
  --password "$KEYCLOAK_ADMIN_PASSWORD"

client_uuid=$("$KCADM" get clients -r "$REALM" -q clientId="$CLIENT_ID" --fields id \
  | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)

if [ -z "$client_uuid" ]; then
  "$KCADM" create clients -r "$REALM" \
    -s clientId="$CLIENT_ID" \
    -s name="Global Exchange Admin API" \
    -s enabled=true \
    -s publicClient=false \
    -s secret="$CLIENT_SECRET" \
    -s serviceAccountsEnabled=true \
    -s standardFlowEnabled=false \
    -s directAccessGrantsEnabled=false \
    -s fullScopeAllowed=false
  client_uuid=$("$KCADM" get clients -r "$REALM" -q clientId="$CLIENT_ID" --fields id \
    | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
else
  "$KCADM" update "clients/$client_uuid" -r "$REALM" \
    -s enabled=true \
    -s publicClient=false \
    -s secret="$CLIENT_SECRET" \
    -s serviceAccountsEnabled=true \
    -s standardFlowEnabled=false \
    -s directAccessGrantsEnabled=false \
    -s fullScopeAllowed=false
fi

realm_management_uuid=$("$KCADM" get clients -r "$REALM" -q clientId=realm-management --fields id \
  | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)

for role in query-users view-users manage-users; do
  "$KCADM" add-roles -r "$REALM" \
    --uusername "service-account-$CLIENT_ID" \
    --cclientid realm-management \
    --rolename "$role"

  # Además de asignarlo a la cuenta de servicio, incluir únicamente este rol
  # en el scope del token emitido para el cliente confidencial.
  role_json=$("$KCADM" get "clients/$realm_management_uuid/roles/$role" -r "$REALM" -c)
  "$KCADM" create "clients/$client_uuid/scope-mappings/clients/$realm_management_uuid" \
    -r "$REALM" -b "[$role_json]"
done

echo "Cliente técnico de Keycloak configurado."
