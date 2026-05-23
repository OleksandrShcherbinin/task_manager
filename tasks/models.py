from django.db import models
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_done', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tasks:detail', args=[self.pk])

    @property
    def is_expired(self):
        return (
            self.due_date is not None
            and not self.is_done
            and self.due_date < timezone.localdate()
        )
