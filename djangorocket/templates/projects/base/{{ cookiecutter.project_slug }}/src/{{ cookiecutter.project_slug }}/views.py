from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def index_view(request):
    return render(request, "pages/index.html")
