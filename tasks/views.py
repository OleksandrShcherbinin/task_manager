import json

from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from .filters import TaskFilter
from .forms import TaskForm
from .models import Task


class TaskListView(FilterView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    filterset_class = TaskFilter

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET
        ctx['priority_choices'] = Task.Priority.choices
        ctx['status_choices'] = [
            ('', 'All'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('expired', 'Expired'),
        ]
        current = {
            'priority': params.get('priority', ''),
            'status': params.get('status', ''),
            'due_from': params.get('due_from', ''),
            'due_to': params.get('due_to', ''),
            'preset': params.get('preset', ''),
        }
        ctx['current'] = current
        ctx['selected_date'] = (
            current['due_from']
            if current['due_from'] and current['due_from'] == current['due_to']
            else ''
        )
        ctx['task_dates_json'] = json.dumps(
            sorted({
                d.isoformat()
                for d in Task.objects.exclude(due_date__isnull=True)
                                     .values_list('due_date', flat=True)
            })
        )
        ctx['today_iso'] = timezone.localdate().isoformat()
        return ctx


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:list')


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')


def toggle_done(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    task = get_object_or_404(Task, pk=pk)
    task.is_done = not task.is_done
    task.save(update_fields=['is_done'])
    next_url = request.POST.get('next') or reverse_lazy('tasks:list')
    return redirect(next_url)
