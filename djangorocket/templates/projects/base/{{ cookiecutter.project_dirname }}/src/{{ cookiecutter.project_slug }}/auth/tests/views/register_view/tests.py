from http import HTTPStatus

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import include, path, reverse


class RegisterViewTests(TestCase):
    urlpatterns = [
        path("", include("{{ cookiecutter.project_slug }}.auth.urls")),
    ]

    def test_endpoint(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        self.assertEqual(url, "/register/")

    def test_get_response_status_code(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_response_context(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
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

        terms_field = form.fields["terms"]
        self.assertTrue(terms_field.required)
        self.assertFalse(terms_field.disabled)

    def test_post_invalid_email_displays_error_message(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        data = {
            "name": "Marie C",
            "email": "marie@example",
            "password": "safsdf678hg",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "Enter a valid email address.",
            html=True,
        )

    def test_post_missing_name_displays_error_message(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        data = {
            "email": "john@example.com",
            "password": "fdsjgkhdfgs",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "You need to enter your name.", html=True)

    def test_post_missing_password_displays_error_message(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        data = {
            "name": "John Smith",
            "email": "john@example.com",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "You need to enter a password.", html=True)

    def test_post_password_with_less_than_8_characters_displays_error_message(self):
        url = reverse("{{cookiecutter.project_slug }}-auth:register")
        data = {
            "name": "Ernesto González",
            "email": "ernesto@example.com",
            "password": "shd72!s",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Your password must have at least 8 characters.", html=True
        )

    def test_post_terms_off_displays_error_message(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "shd72!s",
        }
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "You need to accept the Terms and Conditions.",
            html=True,
        )

    def test_post_success_authenticates_request_user(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "fdg7dsg8sdfg78",
            "terms": "on",
        }
        self.client.post(url, data=data, follow=True)

        self.assertTrue(get_user(self.client).is_authenticated)

    def test_post_success_redirects_to_index(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "fdg7dsg8sdfg78",
            "terms": "on",
        }
        response = self.client.post(url, data=data, follow=False)

        self.assertRedirects(
            response,
            reverse("index"),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
            fetch_redirect_response=True,
        )

    def test_put_is_not_allowed(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        response = self.client.put(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_is_not_allowed(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        response = self.client.patch(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("{{ cookiecutter.project_slug }}-auth:register")
        response = self.client.delete(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
