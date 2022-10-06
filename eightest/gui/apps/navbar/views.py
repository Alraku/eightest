import os
import logging

from runner import main
from utilities import ROOT_DIR
from django.shortcuts import render

log = logging.getLogger('main')


def function(request):
    os.chdir(ROOT_DIR)
    main()
    return render(request, 'home.html')
