from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Max, Min, Count, Q
from django.db.models.functions import TruncMonth

from .models import User, Student, Teacher, Class, Course, Grade
from .forms import (
    LoginForm, StudentRegisterForm, StudentForm, GradeForm, GradeBatchForm,
)
from .decorators import student_required, teacher_required


# ==================== 通用视图 ====================

def user_login(request):
    """登录视图"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"欢迎回来，{user.first_name or user.username}！")
                return redirect("dashboard")
            else:
                messages.error(request, "用户名或密码错误")
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


def user_logout(request):
    """登出"""
    logout(request)
    messages.info(request, "您已安全退出")
    return redirect("login")


@login_required
def dashboard(request):
    """根据角色跳转到对应面板"""
    if request.user.role == "student":
        return redirect("student_dashboard")
    elif request.user.role == "teacher":
        return redirect("teacher_dashboard")
    return redirect("login")


# ==================== 学生端视图 ====================

@login_required
@student_required
def student_dashboard(request):
    """学生面板首页"""
    student = get_object_or_404(Student, user=request.user)
    grades = Grade.objects.filter(student=student).select_related("course")

    # 按课程聚合成绩
    course_grades = {}
    for g in grades:
        if g.course not in course_grades:
            course_grades[g.course] = []
        course_grades[g.course].append(g)

    total_courses = len(course_grades)
    total_grades = grades.count()
    avg_score = grades.aggregate(avg=Avg("score"))["avg"]

    context = {
        "student": student,
        "course_grades": course_grades,
        "total_courses": total_courses,
        "total_grades": total_grades,
        "avg_score": avg_score,
    }
    return render(request, "core/student_dashboard.html", context)


@login_required
@student_required
def student_info(request):
    """查看个人信息"""
    student = get_object_or_404(Student, user=request.user)
    return render(request, "core/student_info.html", {"student": student})


@login_required
@student_required
def student_grades(request):
    """查看个人成绩"""
    student = get_object_or_404(Student, user=request.user)
    grades = Grade.objects.filter(student=student).select_related("course").order_by("course__name", "-exam_type")

    # 按课程分组
    grouped = {}
    for g in grades:
        grouped.setdefault(g.course, []).append(g)

    # 汇总统计
    total_avg = grades.aggregate(avg=Avg("score"))["avg"]

    context = {
        "grouped_grades": grouped,
        "total_avg": total_avg,
    }
    return render(request, "core/student_grades.html", context)


# ==================== 教师端视图 ====================

@login_required
@teacher_required
def teacher_dashboard(request):
    """教师面板首页"""
    teacher = get_object_or_404(Teacher, user=request.user)
    total_students = Student.objects.count()
    total_classes = Class.objects.count()
    total_courses = Course.objects.count()
    recent_grades = Grade.objects.select_related("student", "course").order_by("-created_at")[:10]
    class_list = Class.objects.annotate(student_count=Count("students"))

    context = {
        "teacher": teacher,
        "total_students": total_students,
        "total_classes": total_classes,
        "total_courses": total_courses,
        "recent_grades": recent_grades,
        "class_list": class_list,
    }
    return render(request, "core/teacher_dashboard.html", context)


# ---- 学生管理 ----

@login_required
@teacher_required
def student_list(request):
    """学生列表"""
    students = Student.objects.select_related("user", "class_obj").all()
    class_filter = request.GET.get("class")
    search = request.GET.get("search", "")

    if class_filter:
        students = students.filter(class_obj_id=class_filter)
    if search:
        students = students.filter(
            Q(student_no__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__username__icontains=search)
        )

    classes = Class.objects.all()
    context = {
        "students": students,
        "classes": classes,
        "class_filter": class_filter,
        "search": search,
    }
    return render(request, "core/student_list.html", context)


@login_required
@teacher_required
def student_add(request):
    """添加学生"""
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            # 创建用户
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                messages.error(request, f"用户名 {username} 已存在")
            else:
                user = User.objects.create_user(
                    username=username,
                    password=form.cleaned_data.get("password") or "123456",
                    first_name=form.cleaned_data.get("first_name", ""),
                    phone=form.cleaned_data.get("phone", ""),
                    role="student",
                )
                Student.objects.create(
                    user=user,
                    student_no=form.cleaned_data["student_no"],
                    class_obj=form.cleaned_data.get("class_obj"),
                    gender=form.cleaned_data.get("gender", "男"),
                    birth_date=form.cleaned_data.get("birth_date"),
                    address=form.cleaned_data.get("address", ""),
                    enrollment_date=form.cleaned_data.get("enrollment_date"),
                )
                messages.success(request, f"学生 {username} 添加成功")
                return redirect("student_list")
    else:
        form = StudentForm()
    return render(request, "core/student_form.html", {"form": form, "action": "添加"})


@login_required
@teacher_required
def student_edit(request, pk):
    """编辑学生"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "学生信息更新成功")
            return redirect("student_list")
    else:
        form = StudentForm(instance=student)
    return render(request, "core/student_form.html", {"form": form, "action": "编辑", "student": student})


@login_required
@teacher_required
def student_delete(request, pk):
    """删除学生"""
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, "学生已删除")
    return redirect("student_list")


# ---- 成绩管理 ----

@login_required
@teacher_required
def grade_list(request):
    """成绩列表"""
    grades = Grade.objects.select_related("student", "course").all()
    course_filter = request.GET.get("course")
    class_filter = request.GET.get("class")

    if course_filter:
        grades = grades.filter(course_id=course_filter)
    if class_filter:
        grades = grades.filter(student__class_obj_id=class_filter)

    context = {
        "grades": grades,
        "courses": Course.objects.all(),
        "classes": Class.objects.all(),
        "course_filter": course_filter,
        "class_filter": class_filter,
    }
    return render(request, "core/grade_list.html", context)


@login_required
@teacher_required
def grade_add(request):
    """录入单个成绩"""
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "成绩录入成功")
            return redirect("grade_list")
    else:
        form = GradeForm()
    return render(request, "core/grade_entry.html", {"form": form, "action": "录入"})


@login_required
@teacher_required
def grade_edit(request, pk):
    """编辑成绩"""
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, "成绩更新成功")
            return redirect("grade_list")
    else:
        form = GradeForm(instance=grade)
    return render(request, "core/grade_entry.html", {"form": form, "action": "编辑"})


@login_required
@teacher_required
def grade_batch(request):
    """批量录入成绩"""
    if request.method == "POST":
        form = GradeBatchForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data["course"]
            exam_type = form.cleaned_data["exam_type"]
            class_obj = form.cleaned_data.get("class_obj")

            students = Student.objects.all()
            if class_obj:
                students = students.filter(class_obj=class_obj)

            # 保存表单数据到 session 以在下一步使用
            request.session["batch_course_id"] = course.id
            request.session["batch_exam_type"] = exam_type
            request.session["batch_class_id"] = class_obj.id if class_obj else None

            return render(request, "core/grade_batch_entry.html", {
                "students": students.select_related("user"),
                "course": course,
                "exam_type": exam_type,
            })
    else:
        form = GradeBatchForm()
    return render(request, "core/grade_batch_form.html", {"form": form})


@login_required
@teacher_required
def grade_batch_save(request):
    """保存批量成绩"""
    if request.method != "POST":
        return redirect("grade_batch")

    course_id = request.session.get("batch_course_id")
    exam_type = request.session.get("batch_exam_type")
    if not course_id or not exam_type:
        messages.error(request, "会话已过期，请重新选择")
        return redirect("grade_batch")

    course = get_object_or_404(Course, pk=course_id)
    saved_count = 0

    for key, value in request.POST.items():
        if key.startswith("score_"):
            student_id = key.replace("score_", "")
            score_str = value.strip()
            if score_str:
                try:
                    score = Decimal(score_str)
                    if 0 <= score <= 100:
                        student = get_object_or_404(Student, pk=student_id)
                        Grade.objects.update_or_create(
                            student=student,
                            course=course,
                            exam_type=exam_type,
                            defaults={"score": score},
                        )
                        saved_count += 1
                except (ValueError, Exception):
                    continue

    messages.success(request, f"成功录入 {saved_count} 条成绩")
    return redirect("grade_list")


# ---- 统计 ----

@login_required
@teacher_required
def statistics(request):
    """班级成绩统计"""
    class_id = request.GET.get("class")
    course_id = request.GET.get("course")

    # 所有班级列表
    classes = Class.objects.all()
    courses = Course.objects.all()

    stats = []
    selected_class = None
    selected_course = None

    if class_id:
        selected_class = get_object_or_404(Class, pk=class_id)
        students = Student.objects.filter(class_obj=selected_class)

        if course_id:
            selected_course = get_object_or_404(Course, pk=course_id)
            for student in students:
                grades = Grade.objects.filter(student=student, course=selected_course)
                grade_data = []
                for g in grades.order_by("exam_type"):
                    grade_data.append({"exam_type": g.get_exam_type_display(), "score": g.score})
                avg = grades.aggregate(avg=Avg("score"))["avg"]
                stats.append({
                    "student": student,
                    "grades": grade_data,
                    "avg_score": avg,
                })

    # 班级整体统计
    class_stats = None
    if selected_class and selected_course:
        all_grades = Grade.objects.filter(
            student__class_obj=selected_class, course=selected_course
        )
        class_stats = all_grades.aggregate(
            avg=Avg("score"),
            max=Max("score"),
            min=Min("score"),
            count=Count("id"),
        )
        # 分数段分布
        dist = {
            "优秀 (90-100)": all_grades.filter(score__gte=90).count(),
            "良好 (80-89)": all_grades.filter(score__gte=80, score__lt=90).count(),
            "中等 (70-79)": all_grades.filter(score__gte=70, score__lt=80).count(),
            "及格 (60-69)": all_grades.filter(score__gte=60, score__lt=70).count(),
            "不及格 (<60)": all_grades.filter(score__lt=60).count(),
        }

    context = {
        "classes": classes,
        "courses": courses,
        "selected_class": selected_class,
        "selected_course": selected_course,
        "stats": stats,
        "class_stats": class_stats if class_id and course_id else None,
        "distribution": dist if class_id and course_id else None,
    }
    return render(request, "core/statistics.html", context)
