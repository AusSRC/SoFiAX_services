import os
import functools
import threading
import json

from django.db import connection
from datetime import datetime
from django.http import HttpRequest
from django.db.models.signals import post_delete
from django.dispatch import receiver

from survey.models import Task, TaskReturn


@receiver(post_delete, sender=Task)
def delete_task_hook(sender, instance, using, **kwargs):
    ret = instance.get_return()
    if ret:
        ret.cleanup()

def _thread_func(func, task_id, *args, **kwargs):
    try:
        Task.objects.filter(pk=task_id).update(start=datetime.now(), state='RUNNING')
        if len(args[0]) == 0:
            ret = func()
        else:
            ret = func(*args[0], **kwargs)

        if ret is None:
            ret = NoneTaskReturn()
        elif isinstance(ret, TaskReturn) is False:
            raise Exception(f"{fun.__name__} must return TaskReturn object")

        Task.objects.filter(pk=task_id).update(retval=ret.get_json(), end=datetime.now(), state='COMPLETED')
    except Exception as e:
        Task.objects.filter(pk=task_id).update(error=str(e), state='ERROR')
    
    connection.close()


def task(exclusive_func_with=[]):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            req = None
            for a in args:
                if isinstance(a, HttpRequest):
                    req = a
                    break

            if not req:
                raise ValueError('Must have HttpRequest as argument')

            if isinstance(exclusive_func_with, list) is False:
                raise ValueError('exclusive_func_with must be a list')

            running = Task.objects.filter(func__in=exclusive_func_with, state__in=['PENDING', 'RUNNING'])
            if running.count() > 0:
                raise ValueError(f'Functions {",".join(exclusive_func_with)} is RUNNING or PENDING, please wait for them to finish.')

            # Create new task to track, in PENDING
            t = Task.objects.create(func=func.__name__, args=json.dumps([str(a) for a in args]), state='PENDING', user=req.user.username)
            t.save()

            th = threading.Thread(target=_thread_func, args=(func, t.id, args), kwargs=kwargs, daemon=True)
            th.start()
            return t.id
            
        return wrapper
    return decorator