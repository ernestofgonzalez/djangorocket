from http import HTTPStatus

from django.test import TestCase
from django.urls import include, path, reverse
from barbecue_jam.auth.factories import UserFactory


class LogoutViewTests(TestCase):
    urlpatterns = [
        path("", include("barbecue_jam.auth.urls")),
    ]

    def test_endpoint(self):
        url = reverse("barbecue_jam-auth:logout")
        self.assertEqual(url, "/logout/")

    def test_get_response_status_code(self):
        user = UserFactory()
        self.client.force_login(user)

        url = reverse("barbecue_jam-auth:logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_post_success_redirects_to_index_path(self):
        user = UserFactory()
        self.client.force_login(user)

        url = reverse("barbecue_jam-auth:logout")
        response = self.client.post(url, follow=True)

        self.assertRedirects(
            response,
            reverse("index"),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
            fetch_redirect_response=True,
        )

    def test_post_with_unauthenticated_request_user_redirects_to_login_page(self):
        url = reverse("barbecue_jam-auth:logout")
        response = self.client.post(url, follow=True)

        self.assertRedirects(
            response,
            reverse("barbecue_jam-auth:login"),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
            fetch_redirect_response=True,
        )

    def test_get_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:logout")
        response = self.client.get(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:logout")
        response = self.client.put(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_patch_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:logout")
        response = self.client.patch(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        url = reverse("barbecue_jam-auth:logout")
        response = self.client.delete(url, data={}, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
