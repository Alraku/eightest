from mailbox import linesep
from typing import Any, Dict
from django.shortcuts import render
from utilities import ROOT_DIR
import os
from django.views.generic import TemplateView


class HistoryView(TemplateView):
    template_name = "history.html"
    logs_path = os.path.join(ROOT_DIR, 'logs')
    logs_list = os.listdir(logs_path)
    final_list = []

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        HistoryView.final_list.clear()
        for item in HistoryView.logs_list:
            log_files = os.listdir(os.path.join(ROOT_DIR, 'logs', item))
            HistoryView.final_list.append({item: log_files})

        context = super(HistoryView, self).get_context_data(**kwargs)
        log_file = os.path.join(HistoryView.logs_path, 'test_session_2022-10-16__14-47-26', 'test_center2.log')
        file = open(log_file, 'r')
        lines = file.readlines()
        context['loglines'] = lines
        context['logs'] = HistoryView.final_list
        return context

    def history(self, request):
        return render(request, 'history.html', self.get_context_data())
