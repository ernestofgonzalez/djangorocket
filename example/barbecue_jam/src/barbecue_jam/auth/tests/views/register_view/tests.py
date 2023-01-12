from http import HTTPStatus

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import include, path, reverse


class RegisterViewTests(TestCase):
    urlpatterns = [
        path("", include("barbecue_jam.auth.urls")),
    ]

    def test_endpoint(self):
        url = reverse("barbecue_jam-auth:register")
        self.assertEqual(url, "/register/")

    def test_get_response_status_code(self):
        url = reverse("barbecue_jam-auth:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_response_context(self):
        url = reverse("barbecue_jam-auth:register")
        response = self.client.get(url)

        self.assertIn("form", response.context)

        form = response.context["form"]
        self.assertIn("name", form.fields)
        self.assertIn("email", form.fields)
        self.assertIn("password", form.fields)
        self.assertIn("terms", form.fields)

        name_field = form.fields["name"]
        self.assertTrue(name_field.required)
        self.assertFalse(name_field.disabled)

        email_field = form.fields["email"]
        self.assertTrue(email_field.required)
        self.assertFalse(email_field.disabled)

        password_field = form.fields["password"]
        self.assertTrue(password_field.required)
        self.assertFalse(password_field.disabled)

        country_field = form.fields["country"]
        self.assertTrue(country_field.required)
        self.assertFalse(country_field.disabled)

        terms_field = form.fields["terms"]
        self.assertTrue(terms_field.required)
        self.assertFalse(terms_field.disabled)

    def test_post_invalid_email_displays_error_message(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "name": "Marie C",
            "email": "marie@example",
            "password": "safsdf678hg",
            "country": "ES",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "Este correo electrónico es inválido. Asegúrate de que tenga un formato como este: ana@ejemplo.com",
            html=True,
        )

    def test_post_missing_name_displays_error_message(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "email": "john@example.com",
            "password": "fdsjgkhdfgs",
            "country": "ES",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Es necesario que indiques tu nombre.", html=True)

    def test_post_missing_password_displays_error_message(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "name": "John Smith",
            "email": "john@example.com",
            "country": "ES",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Es necesario que indiques tu password.", html=True
        )

    def test_post_password_with_less_than_8_characters_displays_error_message(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "name": "Ernesto González",
            "email": "ernesto@example.com",
            "password": "shd72!s",
            "country": "ES",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Tu password debe tener al menos 8 caracteres.", html=True
        )

    def test_post_terms_off_displays_error_message(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "shd72!s",
            "country": "ES",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "Debes aceptar los términos y condiciones para poder empezar.",
            html=True,
        )

    def test_post_success_authenticates_request_user(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "fdg7dsg8sdfg78",
            "country": "ES",
            "terms": "on",
        }
        self.client.post(url, data=data, follow=True)

        self.assertTrue(get_user(self.client).is_authenticated)

    def test_post_success_redirects_to_index(self):
        url = reverse("barbecue_jam-auth:register")
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "fdg7dsg8sdfg78",
            "country": "ES",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=False)

        self.assertRedirects(
            response,
            reverse("index"),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.FOUND,
            fetch_redirect_response=True,
        )

    def test_put_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:register")
        response = self.client.put(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:register")
        response = self.client.patch(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:register")
        response = self.client.delete(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
