import serpy


class Serializer(serpy.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(Serializer, self).__init__(*args, **kwargs)

        # If fields is passed, includes only passed fields
        # in the .to_value() step, allowing to skip query/serialize
        # only the necessary fields.
        if fields is not None:
            allowed = set(fields)
            existing = set(self._field_map)
            for field_name in existing - allowed:
                del self._field_map[field_name]
            self._compiled_fields = list(
                filter(lambda x: x[0] in allowed, self._compiled_fields)
            )

        context = kwargs.pop("context", None)
        if context is not None:
            self.context = context
