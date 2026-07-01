from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, Teacher, Class, Course, Grade


class LoginForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=150)
    password = forms.CharField(label="密码", widget=forms.PasswordInput)


class StudentRegisterForm(UserCreationForm):
    student_no = forms.CharField(label="学号", max_length=20)
    full_name = forms.CharField(label="姓名", max_length=30)

    class Meta:
        model = User
        fields = ["username", "full_name", "student_no", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "student"
        user.first_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_no=self.cleaned_data["student_no"],
            )
        return user


class StudentForm(forms.ModelForm):
    username = forms.CharField(label="用户名", max_length=150)
    first_name = forms.CharField(label="姓名", max_length=30, required=False)
    phone = forms.CharField(label="手机号", max_length=20, required=False)
    password = forms.CharField(label="密码", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Student
        fields = ["student_no", "class_obj", "gender", "birth_date", "address", "enrollment_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["username"].initial = self.instance.user.username
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["phone"].initial = self.instance.user.phone
            self.fields["username"].disabled = True

    def save(self, commit=True):
        student = super().save(commit=False)
        if self.instance.pk:
            user = student.user
            user.first_name = self.cleaned_data["first_name"]
            user.phone = self.cleaned_data.get("phone", "")
            pwd = self.cleaned_data.get("password")
            if pwd:
                user.set_password(pwd)
            user.save()
        if commit:
            student.save()
        return student


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["student", "course", "score", "exam_type"]
        widgets = {
            "score": forms.NumberInput(attrs={"step": "0.5", "min": "0", "max": "100"}),
        }


class GradeBatchForm(forms.Form):
    """批量录入成绩"""
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="课程")
    exam_type = forms.ChoiceField(
        choices=Grade._meta.get_field("exam_type").choices, label="考试类型"
    )
    class_obj = forms.ModelChoiceField(
        queryset=Class.objects.all(), label="班级", required=False
    )
