from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import View


class AdminListView(View):

    def get(self, request):
        return HttpResponse("HOLA")

def admin_list_view(request):
    return HttpResponse("Djrill Index")
