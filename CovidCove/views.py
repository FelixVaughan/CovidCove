from django.shortcuts import render

def homepage(request, template_name, **kwargs):
    context = {}
    return render(request, template_name=template_name, context=context)