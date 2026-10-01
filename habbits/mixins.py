from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


class FullCleanMixin:
    Meta: type

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise DRFValidationError(self._format_errors(exc))
        instance.save()
        return instance

    def _format_errors(self, exc: DjangoValidationError) -> dict:
        raise NotImplementedError
