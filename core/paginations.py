from collections import OrderedDict
from django.conf import settings
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class WagtailAPIPagination(BasePagination):
    def paginate_queryset(self, queryset, request, view=None):
        limit_max = getattr(settings, "WAGTAILAPI_LIMIT_MAX", 20)
        limit_default = getattr(settings, "WAGTAILAPI_LIMIT_DEFAULT", 20)

        try:
            offset = int(request.GET.get("offset", 0))
            if offset < 0:
                raise ValueError()
        except ValueError:
            raise ValidationError("offset must be a positive integer")

        try:
            limit = int(request.GET.get("limit", limit_default))
            if limit < 0:
                raise ValueError()
        except ValueError:
            raise ValidationError("limit must be a positive integer")

        if limit_max and limit > limit_max:
            raise ValidationError("limit cannot be higher than %d" % limit_max)

        start = offset
        stop = offset + limit

        self.view = view
        self.total_count = queryset.count()
        return queryset[start:stop]

    def get_paginated_response(self, data):
        data = OrderedDict(
            [
                (
                    "meta",
                    OrderedDict(
                        [
                            ("total_count", self.total_count),
                        ]
                    ),
                ),
                ("items", data),
            ]
        )
        return Response(data)
