import os
import logging
import threading

from runner import Runner
from utilities import ROOT_DIR
from django.shortcuts import render
from django.http.response import JsonResponse

log = logging.getLogger('main')

variable = False
os.chdir(ROOT_DIR)
runner = Runner()


def function(request, context):
    global variable
    variable = True

    # data = request.session.get('my_data')
    # for dat in data:
    #     print(type(dat))
    data = context["xd"]

    runner.collect_tests(data)
    runner.dispatch_tasks()

    try:
        thread = threading.Thread(target=runner.run_tests, args=())
        thread.start()

    except Exception:
        raise Exception

    return render(request, 'home.html')


def answer_me(request):
    if request.method == 'GET':
        global variable
        if variable:
            response = runner.tasks.get_progress()
            return JsonResponse({"name": response, "variable": variable})
        else:
            return JsonResponse({"name": 'xd'})


def playpause(request):
    if request.method == 'GET':
        global variable
        if variable:
            response = runner.pause_resume()
            return render(request, 'home.html')


def reset(request):
    if request.method == 'GET':
        global variable
        if variable:
            response = runner.tasks.reset()
            return render(request, 'home.html')


def chris(request):
    data = {'name': 'chris'}
    return JsonResponse(data)
