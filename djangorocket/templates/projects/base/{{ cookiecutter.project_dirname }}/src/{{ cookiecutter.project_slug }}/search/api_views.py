from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from {{cookiecutter.project_slug}}.permissions import IsConsumerAuthenticated
from {{cookiecutter.project_slug}}.search.serializers import SearchHitSerializer
from {{cookiecutter.project_slug}}.search.utils import search


@api_view(["GET"])
@permission_classes([IsConsumerAuthenticated, IsAuthenticated])
def search_view(request):
    q = request.GET.get("q", None)

    course = request.GET.get("course", None)

    s = search(q, course_uuid=course)
    hits_serializer = SearchHitSerializer(s.hits, many=True)

    return Response(
        {
            "total": len(hits_serializer.data),
            "results": hits_serializer.data,
        },
        status=HTTP_200_OK,
    )
