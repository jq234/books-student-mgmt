"""
初始化测试数据：教师、班级、课程、学生、成绩
运行方式: python manage.py init_data
"""
import sys
import io
from django.core.management.base import BaseCommand
from core.models import User, Teacher, Class, Course, Student, Grade

# 强制 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Command(BaseCommand):
    help = "初始化系统测试数据"

    def handle(self, *args, **options):
        self.stdout.write(">>> 正在初始化测试数据...\n")

        # ===== 教师 =====
        t_users = [
            ("teacher1", "张老师", "教授", "计算机系"),
            ("teacher2", "李老师", "副教授", "数学系"),
            ("teacher3", "王老师", "讲师", "外语系"),
        ]
        teachers = []
        for uname, name, title, dept in t_users:
            u, created = User.objects.get_or_create(
                username=uname, defaults={"first_name": name, "role": "teacher"}
            )
            if created:
                u.set_password("123456")
                u.save()
            t, _ = Teacher.objects.get_or_create(
                user=u,
                defaults={"teacher_no": f"T{1001+len(teachers)}", "title": title, "department": dept},
            )
            teachers.append(t)
            self.stdout.write(f"  [OK] 教师: {uname} ({name}) - 密码: 123456")

        # ===== 班级 =====
        class_data = [
            "计算机1班", "计算机2班",
            "数学1班",
            "英语1班", "英语2班",
        ]
        classes = []
        for name in class_data:
            grade = "2024级" if "数学" not in name else "2023级"
            c, created = Class.objects.get_or_create(name=name, defaults={"grade": grade})
            classes.append(c)
            self.stdout.write(f"  [OK] 班级: {grade} {name}")

        # ===== 课程 =====
        course_data = [
            ("Python程序设计", "CS101", 4.0, teachers[0], "2024-2025-2"),
            ("数据库原理", "CS201", 3.0, teachers[0], "2024-2025-2"),
            ("高等数学", "MATH101", 5.0, teachers[1], "2024-2025-2"),
            ("大学英语", "ENG101", 3.0, teachers[2], "2024-2025-2"),
            ("线性代数", "MATH201", 3.0, teachers[1], "2024-2025-2"),
        ]
        courses = []
        for name, code, credit, t, sem in course_data:
            c, created = Course.objects.get_or_create(
                code=code, defaults={"name": name, "credit": credit, "teacher": t, "semester": sem},
            )
            courses.append(c)
            self.stdout.write(f"  [OK] 课程: {code} {name} ({credit}学分)")

        # ===== 学生 =====
        student_data = [
            ("2024001", "赵小明", classes[0], "男"),
            ("2024002", "钱小红", classes[0], "女"),
            ("2024003", "孙小刚", classes[0], "男"),
            ("2024004", "李小丽", classes[0], "女"),
            ("2024005", "周小强", classes[1], "男"),
            ("2024006", "吴小美", classes[1], "女"),
            ("2024007", "郑小伟", classes[1], "男"),
            ("2024008", "王小芳", classes[1], "女"),
            ("2023001", "陈小宇", classes[2], "男"),
            ("2023002", "林小雨", classes[2], "女"),
            ("2024009", "黄小杰", classes[3], "男"),
            ("2024010", "刘小婷", classes[3], "女"),
            ("2024011", "何小飞", classes[4], "男"),
            ("2024012", "吕小慧", classes[4], "女"),
        ]
        students = []
        for sno, name, cls, gender in student_data:
            uname = f"stu{sno[-3:]}"
            u, created = User.objects.get_or_create(
                username=uname, defaults={"first_name": name, "role": "student"}
            )
            if created:
                u.set_password("123456")
                u.save()
            s, _ = Student.objects.get_or_create(
                user=u, defaults={"student_no": sno, "class_obj": cls, "gender": gender}
            )
            students.append(s)
            self.stdout.write(f"  [OK] 学生: {sno} {name} ({cls.name})")

        # ===== 成绩 =====
        import random
        random.seed(42)

        grade_entries = [
            ([0, 1, 3], range(0, 8), "final"),
            ([0, 1, 3], range(0, 8), "midterm"),
            ([2, 4], range(8, 10), "final"),
            ([2, 4], range(8, 10), "midterm"),
            ([3], range(10, 14), "final"),
            ([3], range(10, 14), "midterm"),
        ]

        grade_count = 0
        for course_idxs, student_range, exam_type in grade_entries:
            for ci in course_idxs:
                course = courses[ci]
                for si in student_range:
                    student = students[si]
                    if student.class_obj.name.startswith("计算机"):
                        score = round(random.uniform(55, 98), 1)
                    elif student.class_obj.name.startswith("数学"):
                        score = round(random.uniform(50, 95), 1)
                    else:
                        score = round(random.uniform(60, 92), 1)

                    Grade.objects.update_or_create(
                        student=student, course=course, exam_type=exam_type,
                        defaults={"score": score},
                    )
                    grade_count += 1

        self.stdout.write(f"\n  [OK] 成绩记录: {grade_count} 条")

        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*50}\n"
            f"初始化完成!\n"
            f"  教师账号: teacher1 / 123456\n"
            f"  学生账号: stu001 / 123456\n"
            f"  所有账号密码均为: 123456\n"
            f"{'='*50}"
        ))
