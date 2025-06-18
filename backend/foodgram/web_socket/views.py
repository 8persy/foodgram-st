from django.shortcuts import render


def websocket_render(request):
    return render(request, "web_socket/index.html")
