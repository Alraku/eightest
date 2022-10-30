import os

from runner import Runner
from utilities import ROOT_DIR
from django.shortcuts import render
from django.http.response import JsonResponse

os.chdir(ROOT_DIR)
runner = Runner()


def home(request):
    context = {"tests": runner.test_tree}
    return render(request, 'home.html', context)


def checkboxes(request):
    lista = request.POST.getlist('checks[]')
    # request.session['my_data'] = lista
    # return render(request, 'home.html')
    return redirect