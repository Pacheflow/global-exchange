from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .keycloak import endpoint


class KeycloakConfigurationTests(TestCase):
    @override_settings(
        KEYCLOAK_SERVER_URL="http://localhost:8080",
        KEYCLOAK_INTERNAL_URL="http://keycloak:8080",
        KEYCLOAK_REALM="global-exchange",
    )
    def test_separates_browser_and_container_urls(self):
        self.assertEqual(endpoint(), "http://localhost:8080/realms/global-exchange")
        self.assertEqual(endpoint(internal=True), "http://keycloak:8080/realms/global-exchange")


class AuthenticationFlowTests(TestCase):
    def test_login_redirects_to_keycloak_with_state(self):
        response = self.client.get(reverse("usuarios:login"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/protocol/openid-connect/auth", response.url)
        self.assertIn("state=", response.url)
        self.assertIn("callback", response.url)

    def test_protected_page_redirects_to_login(self):
        response = self.client.get(reverse("usuarios:dashboard"))
        self.assertRedirects(response, reverse("usuarios:login"), fetch_redirect_response=False)

    @patch("usuarios.views.userinfo")
    @patch("usuarios.views.exchange_code")
    def test_callback_creates_authenticated_session(self, exchange, info):
        exchange.return_value = {"access_token": "access", "id_token": "id"}
        info.return_value = {"sub": "123", "preferred_username": "guille", "email": "guille@example.com"}
        session = self.client.session
        session["oidc_state"] = "safe-state"
        session.save()
        response = self.client.get(reverse("usuarios:callback"), {"state": "safe-state", "code": "code"})
        self.assertRedirects(response, reverse("usuarios:dashboard"), fetch_redirect_response=False)
        self.assertEqual(self.client.session["kc_user"]["preferred_username"], "guille")

    def test_callback_rejects_invalid_state(self):
        response = self.client.get(reverse("usuarios:callback"), {"state": "attacker", "code": "code"})
        self.assertEqual(response.status_code, 400)


class ClientContextTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["kc_user"] = {"preferred_username": "guille", "clientes": ["acme-sa", "demo-srl"]}
        session["kc_access_token"] = "access"
        session.save()

    def test_selects_an_associated_client(self):
        response = self.client.post(reverse("usuarios:clients"), {"cliente": "acme-sa"})
        self.assertRedirects(response, reverse("usuarios:dashboard"), fetch_redirect_response=False)
        self.assertEqual(self.client.session["selected_client"]["id"], "acme-sa")

    def test_dashboard_renders_the_user_name(self):
        response = self.client.get(reverse("usuarios:dashboard"))
        self.assertContains(response, "Hola, guille")
        self.assertNotContains(response, "{{ request.session")

    def test_authenticated_home_redirects_to_dashboard(self):
        response = self.client.get(reverse("usuarios:home"))
        self.assertRedirects(response, reverse("usuarios:dashboard"), fetch_redirect_response=False)

    def test_rejects_unassociated_client(self):
        self.client.post(reverse("usuarios:clients"), {"cliente": "other"})
        self.assertNotIn("selected_client", self.client.session)


class UserManagementViewTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["kc_user"] = {"preferred_username": "admin"}
        session["kc_access_token"] = "access"
        session.save()

    @patch("usuarios.views.admin_request")
    def test_edit_user_get_renders_keycloak_values(self, admin_request):
        admin_request.return_value = {
            "id": "user-123",
            "username": "guille",
            "firstName": "Guillermo",
            "lastName": "Benítez",
            "email": "guille@example.com",
            "enabled": True,
        }

        response = self.client.get(reverse("usuarios:edit", args=["user-123"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Guillermo"')
        self.assertContains(response, 'value="Benítez"')
        self.assertContains(response, 'value="guille@example.com"')
