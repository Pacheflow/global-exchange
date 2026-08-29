from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
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


@override_settings(SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies")
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

    def test_rejects_unassociated_client(self):
        self.client.post(reverse("usuarios:clients"), {"cliente": "other"})
        self.assertNotIn("selected_client", self.client.session)
