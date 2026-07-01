from django.urls import path
from . import views

urlpatterns = [
    # 通用
    path("", views.dashboard, name="dashboard"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # 学生端
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/info/", views.student_info, name="student_info"),
    path("student/grades/", views.student_grades, name="student_grades"),

    # 教师端 - 面板
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),

    # 教师端 - 学生管理
    path("teacher/students/", views.student_list, name="student_list"),
    path("teacher/students/add/", views.student_add, name="student_add"),
    path("teacher/students/edit/<int:pk>/", views.student_edit, name="student_edit"),
    path("teacher/students/delete/<int:pk>/", views.student_delete, name="student_delete"),

    # 教师端 - 成绩管理
    path("teacher/grades/", views.grade_list, name="grade_list"),
    path("teacher/grades/add/", views.grade_add, name="grade_add"),
    path("teacher/grades/edit/<int:pk>/", views.grade_edit, name="grade_edit"),
    path("teacher/grades/batch/", views.grade_batch, name="grade_batch"),
    path("teacher/grades/batch/save/", views.grade_batch_save, name="grade_batch_save"),

    # 教师端 - 统计
    path("teacher/statistics/", views.statistics, name="statistics"),
]
