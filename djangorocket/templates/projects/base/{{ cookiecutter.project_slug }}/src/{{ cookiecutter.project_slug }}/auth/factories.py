from factory import Faker
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = "{{ cookiecutter.project_slug }}_auth.User"

    name = Faker("name")
    email = Faker("email")
    phone_number = Faker("phone_number")
