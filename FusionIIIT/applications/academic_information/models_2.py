from django.db import models

from applications.globals.models import ExtraInfo


class Constants:
    HOLIDAY_TYPE = (
        ('restricted', 'restricted'),
        ('closed', 'closed'),
        ('vacation', 'vacation')
    )

    ATTEND_CHOICES = (
        ('present', 'present'),
        ('absent', 'absent')
    )

    BRANCH = (
        ('CSE','CSE'),
        ('ECE','ECE'),
        ('ME','ME'),
        ('Design','Design'),
        ('Common','Common'),
    )

    PROGRAMME = (
        ('B.Tech', 'B.Tech'),
        ('B.Des', 'B.Des'),
        ('M.Tech', 'M.Tech'),
        ('M.Des', 'M.Des'),
        ('PhD', 'PhD')
    )

    CATEGORY = (
        ('GEN', 'General'),
        ('SC', 'Scheduled Castes'),
        ('ST', 'Scheduled Tribes'),
        ('OBC', 'Other Backward Classes')
    )

    MTechSpecialization = (
        ('Power and Control', 'Power and Control'),
        ('Microwave and Communication Engineering', 'Microwave and Communication Engineering'),
        ('Micro-nano Electronics', 'Micro-nano Electronics'),
        ('CAD/CAM', 'CAD/CAM'),
        ('Design', 'Design'),
        ('Manufacturing', 'Manufacturing'),
        ('CSE', 'CSE'),
        ('Mechatronics', 'Mechatronics'),
        ('MDes', 'MDes'),
        ('None', 'None')
    )

    COURSE_TYPE = (
        ('Professional Core', 'Professional Core'),
        ('Professional Elective', 'Professional Elective'),
        ('Professional Lab', 'Professional Lab'),
        ('Engineering Science', 'Engineering Science'),
        ('Natural Science', 'Natural Science'),
        ('Humanities', 'Humanities'),
        ('Design', 'Design'),
        ('Manufacturing', 'Manufacturing'),
        ('Management Science', 'Management Science'),
    )


class Student(models.Model):
    id = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE, primary_key=True)
    programme = models.CharField(max_length=10, choices=Constants.PROGRAMME)
    batch = models.IntegerField(default=2016)
    cpi = models.FloatField(default=0)
    category = models.CharField(max_length=10, choices=Constants.CATEGORY, null=False)
    father_name = models.CharField(max_length=40, default='')
    mother_name = models.CharField(max_length=40, default='')
    hall_no = models.IntegerField(default=1)
    room_no = models.CharField(max_length=10, blank=True, null=True)
    specialization = models.CharField(max_length=20,
                                      choices=Constants.MTechSpecialization, null=True)

    def __str__(self):
        return str(self.id)


class Course(models.Model):
    course_id = models.CharField(max_length=100, unique=True)
    course_name = models.CharField(max_length=100)
    credits = models.IntegerField()
    course_details = models.TextField(max_length=200)

    class Meta:
        db_table = 'Course'
        unique_together = ('course_id', 'course_name')

    def __str__(self):
        return self.course_name


class Curriculum(models.Model):
    curriculum_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course)
    course_type = models.CharField(choices=Constants.COURSE_TYPE, max_length=20)
    programme = models.CharField(choices=Constants.PROGRAMME, max_length=10)
    branch = models.CharField(choices=Constants.BRANCH, max_length=10, default='Common')
    batch = models.IntegerField()
    sem = models.IntegerField()

    class Meta:
        db_table = 'Curriculum'

    def __str__(self):
        return str(self.curriculum_id)


class Instructor(models.Model):
    curriculum_id = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    instructor_id = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Instructor'
        unique_together = ('curriculum_id', 'instructor_id')

    def __self__(self):
        return '{} - {}'.format(self.curriculum_id, self.instructor_id)


class Student_attendance(models.Model):
    student_id = models.ForeignKey(Student)
#    course_id = models.ForeignKey(Course)
#    attend = models.CharField(max_length=6, choices=Constants.ATTEND_CHOICES)
    instructor_id = models.ForeignKey(Instructor, on_delete=models.CASCADE)
#    curriculum_id = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=False)

    class Meta:
        db_table = 'Student_attendance'

    def __self__(self):
        return self.course_id


class Meeting(models.Model):
    venue = models.CharField(max_length=50)
    date = models.DateField()
    time = models.CharField(max_length=20)
    agenda = models.TextField()
    minutes_file = models.CharField(max_length=40)

    class Meta:
        db_table = 'Meeting'

    def __str__(self):
        return self.date


class Calendar(models.Model):
    from_date = models.DateField()
    to_date = models.DateField()
    description = models.CharField(max_length=40)

    class Meta:
        db_table = 'Calendar'

    def __str__(self):
        return self.description


class Holiday(models.Model):
    holiday_date = models.DateField()
    holiday_name = models.CharField(max_length=40)
    holiday_type = models.CharField(default='restricted', max_length=30,
                                    choices=Constants.HOLIDAY_TYPE)

    class Meta:
        db_table = 'Holiday'

    def __str__(self):
        return self.holiday_name


class Grades(models.Model):
    student_id = models.ForeignKey(Student)
    course_id = models.ForeignKey(Course)
    sem = models.IntegerField()
    grade = models.CharField(max_length=4)

    class Meta:
        db_table = 'Grades'


class Spi(models.Model):
    sem = models.IntegerField()
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    spi = models.FloatField(default=0)

    class Meta:
        db_table = 'Spi'
        unique_together = ('student_id', 'sem')

    def __self__(self):
        return self.sem


class Timetable(models.Model):
    upload_date = models.DateTimeField(auto_now_add=True)
    time_table = models.FileField(upload_to='Academic_information/Timetable')
    year = models.IntegerField(default="2015")
    programme = models.CharField(max_length=30, default="B.Tech")

    class Meta:
        db_table = 'Timetable'


class Exam_timetable(models.Model):
    upload_date = models.DateField(auto_now_add=True)
    exam_time_table = models.FileField(upload_to='Academic_information/Exam_timetable')
    year = models.IntegerField(default="2015")
    programme = models.CharField(max_length=30, default="B.Tech")

    class Meta:
        db_table = 'Exam_Timetable'
