from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def student_required(view_func):
    """要求学生角色"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "student":
            return view_func(request, *args, **kwargs)
        messages.error(request, "请使用学生账号登录")
        return redirect("login")
    return wrapper


def teacher_required(view_func):
    """要求教师角色"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "teacher":
            return view_func(request, *args, **kwargs)
        messages.error(request, "请使用教师账号登录")
        return redirect("login")
    return wrapper
