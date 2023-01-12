from http import HTTPStatus

from django.test import TestCase
from django.urls import include, path, reverse
from barbecue_jam.auth.factories import UserFactory


class LoginViewTests(TestCase):
    urlpatterns = [
        path("", include("barbecue_jam.auth.urls")),
    ]

    def test_endpoint(self):
        url = reverse("barbecue_jam-auth:login")
        self.assertEqual(url, "/login/")

    def test_get_response_status_code(self):
        url = reverse("barbecue_jam-auth:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_response_context(self):
        url = reverse("barbecue_jam-auth:login")
        response = self.client.get(url)

        self.assertIn("form", response.context)

        form = response.context["form"]
        self.assertIn("email", form.fields)
        self.assertIn("password", form.fields)

        email_field = form.fields["email"]
        self.assertTrue(email_field.required)
        self.assertFalse(email_field.disabled)

        password_field = form.fields["password"]
        self.assertTrue(password_field.required)
        self.assertFalse(password_field.disabled)

    def test_post_invalid_email_displays_error_message(self):
        url = reverse("barbecue_jam-auth:login")
        data = {"email": "john@example", "password": "safsdf678hg"}
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "Este correo electrónico es inválido. Asegúrate de que tenga un formato como este: ana@ejemplo.com",
            html=True,
        )

    def test_post_missing_password_displays_error_message(self):
        url = reverse("barbecue_jam-auth:login")
        data = {
            "email": "john@example",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Es necesario que indiques tu password.", html=True
        )

    def test_post_success_authenticates_request_user(self):
        user = UserFactory(email="john@example.com")
        password = "f7s8tsda87fgyfsads7f"
        user.set_password(password)
        user.save()

        url = reverse("barbecue_jam-auth:login")
        data = {"email": user.email, "password": password}
        self.client.post(url, data=data, follow=True)

        self.assertTrue(user.is_authenticated)

    def test_post_success_redirects_to_index(self):
        user = UserFactory(email="john@example.com")
        password = "f7s8tsda87fgyfsads7f"
        user.set_password(password)
        user.save()

        url = reverse("barbecue_jam-auth:login")
        data = {"email": user.email, "password": password}
        response = self.client.post(url, data=data, follow=False)

        self.assertRedirects(
            response,
            reverse("index"),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.FOUND,
            fetch_redirect_response=True,
        )

    def test_put_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:login")
        response = self.client.put(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:login")
        response = self.client.patch(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:login")
        response = self.client.delete(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
