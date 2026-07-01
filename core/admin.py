from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher, Class, Course, Grade

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "role", "phone", "is_active"]
    list_filter = ["role", "is_active"]
    fieldsets = UserAdmin.fieldsets + (("角色信息", {"fields": ("role", "phone")}),)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ["name", "grade", "created_at"]
    search_fields = ["name", "grade"]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["student_no", "user", "class_obj", "gender", "enrollment_date"]
    search_fields = ["student_no", "user__username", "user__first_name"]
    list_filter = ["class_obj", "gender"]

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["teacher_no", "user", "title", "department"]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "credit", "teacher", "semester"]
    search_fields = ["name", "code"]

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "score", "exam_type", "created_at"]
    list_filter = ["exam_type", "course"]
    search_fields = ["student__student_no", "course__name"]
