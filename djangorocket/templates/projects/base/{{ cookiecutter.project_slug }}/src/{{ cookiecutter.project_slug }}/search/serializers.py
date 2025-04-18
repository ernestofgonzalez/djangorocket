import serpy

from {{cookiecutter.project_slug}}.serializers import Serializer


class SearchHitSerializer(Serializer):
    id = serpy.Field()
    type = serpy.Field()

    def _serialize(self, instance, fields=None):
        # Dynamically select the appropriate serializer based on the 'type' field
        type_to_serializer = {
            # NOTE: include a map from instance.type to respective serializer class
        }

        serializer_class = type_to_serializer.get(instance["type"])
        if not serializer_class:
            raise ValueError(f"Unknown type: {instance['type']}")

        serialized_data = {
            "id": instance["uuid"],
            "type": instance["type"],
            **serializer_class(instance).data
        }

        return serialized_data
