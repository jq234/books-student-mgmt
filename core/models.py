from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型，区分学生和教师角色"""
    ROLE_CHOICES = (
        ("student", "学生"),
        ("teacher", "教师"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    phone = models.CharField(max_length=20, blank=True, verbose_name="手机号")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Class(models.Model):
    """班级"""
    name = models.CharField(max_length=50, unique=True, verbose_name="班级名称")
    grade = models.CharField(max_length=20, verbose_name="年级")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "班级"
        verbose_name_plural = "班级"
        ordering = ["grade", "name"]

    def __str__(self):
        return f"{self.grade} {self.name}"


class Student(models.Model):
    """学生信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    student_no = models.CharField(max_length=20, unique=True, verbose_name="学号")
    class_obj = models.ForeignKey(
        Class, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="students", verbose_name="所属班级"
    )
    gender = models.CharField(
        max_length=4,
        choices=(("男", "男"), ("女", "女")),
        default="男",
        verbose_name="性别",
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="出生日期")
    address = models.CharField(max_length=200, blank=True, verbose_name="家庭住址")
    enrollment_date = models.DateField(null=True, blank=True, verbose_name="入学日期")

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = "学生"
        ordering = ["student_no"]

    def __str__(self):
        return f"{self.student_no} {self.user.get_full_name()}"


class Teacher(models.Model):
    """教师信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    teacher_no = models.CharField(max_length=20, unique=True, verbose_name="工号")
    title = models.CharField(max_length=50, blank=True, verbose_name="职称")
    department = models.CharField(max_length=100, blank=True, verbose_name="所属院系")

    class Meta:
        verbose_name = "教师"
        verbose_name_plural = "教师"

    def __str__(self):
        return f"{self.teacher_no} {self.user.get_full_name()}"


class Course(models.Model):
    """课程"""
    name = models.CharField(max_length=100, verbose_name="课程名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="课程编号")
    credit = models.DecimalField(max_digits=3, decimal_places=1, default=2.0, verbose_name="学分")
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="courses", verbose_name="授课教师"
    )
    semester = models.CharField(max_length=20, verbose_name="学期", default="2025-2026-2")

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"

    def __str__(self):
        return self.name


class Grade(models.Model):
    """成绩"""
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="grades", verbose_name="学生"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="grades", verbose_name="课程"
    )
    score = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="分数")
    exam_type = models.CharField(
        max_length=20,
        choices=(
            ("midterm", "期中"),
            ("final", "期末"),
            ("makeup", "补考"),
            ("daily", "平时"),
        ),
        default="final",
        verbose_name="考试类型",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "成绩"
        verbose_name_plural = "成绩"
        unique_together = ["student", "course", "exam_type"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.student_no} {self.course.name}: {self.score}"
