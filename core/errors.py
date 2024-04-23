from django.shortcuts import render

def handler400(request, exception):
    response = render(request, '400.html')
    response.status_code = 400
    return response

def handler500(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response