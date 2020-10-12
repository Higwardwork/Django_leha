from django.core.serializers import register_serializer

register_serializer('json-no-escape', 'serializers.json_no_escape')
