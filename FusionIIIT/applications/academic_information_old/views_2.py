import datetime
import json
import os
import xlrd
from io import BytesIO
from xlsxwriter.workbook import Workbook
from xhtml2pdf import pisa
from itertools import chain

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

from applications.academic_procedures.models import MinimumCredits, Register, InitialRegistrations
from applications.globals.models import (Designation, ExtraInfo,
                                         HoldsDesignation, DepartmentInfo)

from .forms import AcademicTimetableForm, ExamTimetableForm, MinuteForm
from .models import (Calendar, Course, Exam_timetable, Grades, Curriculum_Instructor,Constants,
                     Meeting, Student, Student_attendance, Timetable,Curriculum)


def homepage(request):
    """
    This function is used to set up the homepage of the application.
    It checkes the authentication of the user and also fetches the available
    data from the databases to display it on the page.

    @param:
        request - contains metadata about the requested page

    @variables:
        senates - the extraInfo objects that holds the designation as a senator
        students - all the objects in the Student class
        Convenor - the extraInfo objects that holds the designation as a convenor
        CoConvenor - the extraInfo objects that holds the designation as a coconvenor
        meetings - the all meeting objects held in senator meetings
        minuteForm - the form to add a senate meeting minutes
        acadTtForm - the form to add academic calender
        examTtForm - the form required to add exam timetable
        Dean - the extraInfo objects that holds the designation as a dean
        student - the students as a senator
        extra - all the extraInfor objects
        exam_t - all the exam timetable objects
        timetable - all the academic timetable objects
        calendar - all the academic calender objects
        department - all the departments in the college
        attendance - all the attendance objects of the students
        context - the datas to be displayed in the webpage

    """
   
    current_user = get_object_or_404(User, username=request.user.username)
    user_details = ExtraInfo.objects.all().filter(user=current_user).first()
    desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
    temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
    #print (temp)
    #print (current_user)
    acadadmin = temp.working
    k = str(user_details).split()
    #print(k)
    final_user = k[2]

    if (str(acadadmin) != str(final_user)):
      return HttpResponseRedirect('/academic-procedures/')
    minuteForm = MinuteForm()
    examTtForm = ExamTimetableForm()
    acadTtForm = AcademicTimetableForm()
    calendar = Calendar.objects.all()

    course_list = sem_for_generate_sheet()
    #print(course_list)

    this_sem_courses = Curriculum.objects.all().filter(sem__in=course_list).filter(floated=True)
    #print(this_sem_courses)

    if(course_list[0]==1):
        course_list = [2, 4, 6, 8]
    else:
        course_list = [1, 3, 5, 7]
    
    next_sem_courses = Curriculum.objects.all().filter(sem__in=course_list).filter(floated=True)
    #print(next_sem_courses)

    courses = Course.objects.all()
    course_type = Constants.COURSE_TYPE
    timetable = Timetable.objects.all()
    exam_t = Exam_timetable.objects.all()

    try:
        senator_des = Designation.objects.get(name='senate')
        convenor_des = Designation.objects.get(name='Convenor')
        coconvenor_des = Designation.objects.get(name='Co Convenor')
        dean_des = Designation.objects.get(name='Dean')
        senates = ExtraInfo.objects.filter(designation=senator_des)
        Convenor = ExtraInfo.objects.filter(designation=convenor_des)
        CoConvenor = ExtraInfo.objects.filter(designation=coconvenor_des)
        Dean = ExtraInfo.objects.get(designation=dean_des)
        students = Student.objects.filter(id__in=senates)
        meetings = Meeting.objects.all()
        student = Student.objects.all()
        extra = ExtraInfo.objects.all()
        courses = Course.objects.all()
        course_type = Constants.COURSE_TYPE
        timetable = Timetable.objects.all()
        exam_t = Exam_timetable.objects.all()
        grade = Grades.objects.all()
    except:
        senates = ""
        students = ""
        Convenor = ""
        CoConvenor = ""
        meetings = ""
        Dean = ""
        student = ""
        grade = ""
        #courses = ""
        extra = ""
        #exam_t = ""
        #timetable = ""
        #curriculum = "=------===----"
        pass

    context = {
         'senates': senates,
         'students': students,
         'Convenor': Convenor,
         'CoConvenor': CoConvenor,
         'meetings': meetings,
         'minuteForm': minuteForm,
         'acadTtForm': acadTtForm,
         'examTtForm': examTtForm,
         'Dean': Dean,
         'student': student,
         'extra': extra,
         'grade': grade,
         'courses': courses,
         'course_type': course_type,
         'exam': exam_t,
         'timetable': timetable,
         'academic_calendar': calendar,
         'next_sem_course': next_sem_courses,
         'this_sem_course': this_sem_courses,
         'curriculum': curriculum,
         'tab_id': ['1','1'],
    }

    return render(request, "ais/ais.html", context)

# ##########curriculum ###############


def curriculum(request):
    context={
            'tab_id' :['3','1']
        }
    if request.method == 'POST':
        print(request.POST)
        try:
            request_batch = request.POST['batch']
            request_branch = request.POST['branch']
            request_programme = request.POST['programme']
            request_sem = request.POST['sem']
        except:
            request_batch = ""
            request_branch = ""
            request_programme = ""
            request_sem = ""
        #for checking if the user has searched for any particular curriculum
        if request_batch == "" and request_branch == "" and request_programme=="" and request_sem=="":
            curriculum = None   #Curriculum.objects.all()
        else:
            print(request_branch,end=" ")
            print(request_batch,end=" ")
            print(request_programme,end=" ")
            print(request_sem)
            if int(request_sem) == 0:
                curriculum = Curriculum.objects.filter(branch = request_branch).filter(batch = request_batch).filter(programme= request_programme).order_by('sem')
            else:
                curriculum = Curriculum.objects.filter(branch = request_branch).filter(batch = request_batch).filter(programme= request_programme).filter(sem= request_sem)
        courses = Course.objects.all()
        course_type = Constants.COURSE_TYPE
        print(curriculum)
        # html = render_to_string("ais/curriculum_list.html", {'curriculum': curriculum}, request)
        # html_js = render_to_string("ais/curriculum_list_js.html", {'curriculum': curriculum}, request)
        # data = {'html':html,
        #         'html_js':html_js,
        #         }
        # obj = json.dumps(data)
        # return HttpResponse(obj, content_type='application/json')
        context={
            'courses' : courses,
            'course_type' : course_type,
            'curriculum' : curriculum,
            'tab_id' :['3','1']
        }
        return render(request, "ais/ais.html", context)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def add_curriculum(request):
    context={
            'tab_id' :['3','2']
        }
    if request.method == 'POST':
        print(request.POST)
        print(type(request.POST))
        i=0
        while True:
            if "semester_"+str(i) in request.POST:
                programme=request.POST['AddProgramme']
                batch=request.POST['AddBatch']
                branch=request.POST['AddBranch']
                sem=request.POST["semester_"+str(i)]
                course_code=request.POST["course_code_"+str(i)]
                course_name=request.POST["course_name_"+str(i)]
                course_id=Course.objects.get(course_name=course_name)
                credits=request.POST["credits_"+str(i)]
                if "optional_"+str(i) in request.POST:
                    optional=True
                else:
                    optional=False
                course_type=request.POST["course_type_"+str(i)]
                print(programme,batch,branch,sem,course_code,course_id,credits,optional,course_type)
                ins=Curriculum.objects.create(
                    programme=programme,
                    batch=batch,
                    branch=branch,
                    sem=sem,
                    course_code=course_code,
                    course_id=course_id,
                    credits=credits,
                    optional=optional,
                    course_type=course_type,
                )
            else:
                print("Khatam")
                break
            i+=1
        curriculum = Curriculum.objects.filter(branch = branch).filter(batch = batch).filter(programme= programme)
        courses = Course.objects.all()
        course_type = Constants.COURSE_TYPE
        context= {
            'courses': courses,
            'course_type': course_type,
            'curriculum': curriculum,
            'tab_id' :['3','2']
        }
        return render(request, "ais/ais.html", context)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def edit_curriculum(request):
    context={
            'tab_id' :['3','1']
        }
    if request.method == 'POST':
        print("edit_curriculum")
        print(request.POST)
        id=request.POST['id']
        programme=request.POST['programme']
        batch=request.POST['batch']
        branch=request.POST['branch']
        sem=request.POST["sem"]
        course_code=request.POST["course_code"]
        course_name=request.POST["course_id"]
        course_id=Course.objects.get(course_name=course_name)
        credits=request.POST["credits"]
        if request.POST['optional'] == "on":
            optional=True
        else:
            optional=False
        course_type=request.POST["course_type"]

        entry=Curriculum.objects.all().filter(curriculum_id=id).first()
        entry.programme=programme
        entry.batch=batch
        entry.branch=branch
        entry.sem=sem
        entry.course_code=course_code
        entry.course_id=course_id
        entry.credits=credits
        entry.optional=optional
        entry.course_type=course_type
        entry.save()
        curriculum = Curriculum.objects.filter(branch = branch).filter(batch = batch).filter(programme= programme)
        courses = Course.objects.all()
        course_type = Constants.COURSE_TYPE
        context= {
            'courses': courses,
            'course_type': course_type,
            'curriculum': curriculum,
            'tab_id' :['3','1']
        }
        return render(request, "ais/ais.html", context)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def delete_curriculum(request):
    context={
            'tab_id' :['3','1']
        }
    if request.method == "POST":
        print("delete_curriculum")
        print (request.POST)
        dele = Curriculum.objects.filter(curriculum_id=request.POST['id'])
        dele.delete()
        curriculum = Curriculum.objects.filter(branch = request.POST['branch']).filter(batch = request.POST['batch']).filter(programme= request.POST['programme'])
        courses = Course.objects.all()
        course_type = Constants.COURSE_TYPE
        context= {
            'courses': courses,
            'course_type': course_type,
            'curriculum': curriculum,
            'tab_id' :['3','1']
        }
        return render(request, "ais/ais.html", context)
    return render(request, 'ais/ais.html', context)


def next_curriculum(request):
    if request.method == 'POST':
        print (request.POST)
        programme = request.POST['programme']
        now = datetime.datetime.now()
        year = int(now.year)
        batch = year-1
        curriculum = Curriculum.objects.all().filter(batch = batch).filter(programme = programme)
        print(curriculum)
        if request.POST['option'] == '1':
            for i in curriculum:
                # print(i.programme,end=" ")
                # print(i.batch+1,end=" ")
                # print(i.branch,end=" ")
                # print(i.sem,end=" ")
                # print(i.course_code,end=" ")
                # print(i.course_id,end=" ")
                # print(i.credits,end=" ")
                # print(i.optional,end=" ")
                # print(i.course_type)
                ins=Curriculum.objects.create(
                    programme=i.programme,
                    batch=i.batch+1,
                    branch=i.branch,
                    sem=i.sem,
                    course_code=i.course_code,
                    course_id=i.course_id,
                    credits=i.credits,
                    optional=i.optional,
                    course_type=i.course_type,
                )

        elif request.POST['option'] == '2':
            for i in curriculum:
                ins=Curriculum.objects.create(
                    programme=i.programme,
                    batch=i.batch+1,
                    branch=i.branch,
                    sem=i.sem,
                    course_code=i.course_code,
                    course_id=i.course_id,
                    credits=i.credits,
                    optional=i.optional,
                    course_type=i.course_type,
                )
            batch=batch+1
            curriculum = Curriculum.objects.all().filter(batch = batch).filter(programme = programme)
            context= {
                'curriculumm' :curriculum,
                'tab_id' :['3','3']
            }
            return render(request, "ais/ais.html", context)
        else:
            context= {
            'tab_id' :['3','2']
            }
            return render(request, "ais/ais.html", context)
    context= {
    'tab_id' :['3','1']
    }
    return render(request, "ais/ais.html", context)


def verify_grade(request):
    """
    It adds the grade of the student

    @param:
        request - contains metadata about the requested page

    @variables:
        current_user - father's name of the student
        user_details - the rollno of the student required to check if the student is available
        desig_id - mother's name of the student
        acadadmin - student's address
        subject - subject of which the grade has to be added
        sem - semester of the student
        grade - grade to be added in the student
        course - course ofwhich the grade is added
    """

    if request.method == "POST":
        curr_id=request.POST['course']
        print(curr_id)
        curr_course = Curriculum.objects.filter(curriculum_id=curr_id)
        grades = Grades.objects.filter(curriculum_id=curr_course)
        context= {
            'grades': grades,
            'tab_id' :"2"
        }
        return render(request,"ais/ais.html", context)
    else:
        return HttpResponseRedirect('/aims/')
    return HttpResponseRedirect('/aims/')


def confirm_grades(request):
    if request.method == "POST":
        print("confirm hone wala hai")
        print(request.POST)
    return HttpResponseRedirect('/aims/')


def add_timetable(request):
    """
    acad-admin can upload the time table(any type of) of the semester.

    @param:
        request - contains metadata about the requested page.

    @variables:
        acadTtForm - data of delete dictionary in post request
    """
    timetable = Timetable.objects.all()
    exam_t = Exam_timetable.objects.all()
    context= {
        'exam': exam_t,
        'timetable': timetable,
        'tab_id' :['10','1']
    }
    acadTtForm = AcademicTimetableForm()
    if request.method == 'POST' and request.FILES:
        acadTtForm = AcademicTimetableForm(request.POST, request.FILES)
        print (acadTtForm)
        if acadTtForm.is_valid():
             acadTtForm.save()
        return render(request, "ais/ais.html", context)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def add_exam_timetable(request):
    """
    acad-admin can upload the exam timtable of the ongoing semester.

    @param:
        request - contains metadata about the requested page.

    @variables:
        examTtForm - data of delete dictionary in post request
    """
    timetable = Timetable.objects.all()
    exam_t = Exam_timetable.objects.all()
    context= {
        'exam': exam_t,
        'timetable': timetable,
        'tab_id' :['10','2']
    }
    examTtForm = ExamTimetableForm()
    if request.method == 'POST' and request.FILES:
        print(request.POST)
        print(request.FILES)
        examTtForm = ExamTimetableForm(request.POST, request.FILES)
        if examTtForm.is_valid():
            print("kkk")
            examTtForm.save()
        return render(request, "ais/ais.html", context)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def delete_timetable(request):
    """
    acad-admin can delete the outdated timetable from the server.

    @param:
        request - contains metadata about the requested page.

    @variables:
        data - data of delete dictionary in post request
        t - Object of time table to be deleted
    """
    if request.method == "POST":
        data = request.POST['delete']
        t = Timetable.objects.get(time_table=data)
        t.delete()
        return HttpResponse("TimeTable Deleted")


def delete_exam_timetable(request):
    """
    acad-admin can delete the outdated exam timetable.

    @param:
        request - contains metadata about the requested page.

    @variables:
        data - data of delete dictionary in post request
        t - Object of Exam time table to be deleted
    """
    if request.method == "POST":
        data = request.POST['delete']
        t = Exam_timetable.objects.get(exam_time_table=data)
        t.delete()
        return HttpResponse("TimeTable Deleted")


def add_calendar(request):
    """
    to add an entry to the academic calendar to be uploaded

    @param:
        request - contains metadata about the requested page.

    @variables:
        from_date - The starting date for the academic calendar event.
        to_date - The ending date for the academic caldendar event.
        desc - Description for the academic calendar event.
        c = object to save new event to the academic calendar.
    """
    calendar = Calendar.objects.all()
    context= {
        'academic_calendar' :calendar,
        'tab_id' :['4','1']
    }
    if request.method == "POST":
        print("Requested Method: ", request.POST)
        from_date = request.POST.getlist('from_date')
        to_date = request.POST.getlist('to_date')
        desc = request.POST.getlist('description')[0]
        print(from_date, to_date, desc)
        from_date = from_date[0].split('-')
        from_date = [int(i) for i in from_date]
        from_date = datetime.datetime(*from_date).date()
        to_date = to_date[0].split('-')
        to_date = [int(i) for i in to_date]
        to_date = datetime.datetime(*to_date).date()
        print(from_date, to_date, desc)
        c = Calendar(
            from_date=from_date,
            to_date=to_date,
            description=desc)
        print(c)
        c.save()
        HttpResponse("Calendar Added")

    return render(request, "ais/ais.html", context)


def update_calendar(request):
    """
    to update an entry to the academic calendar to be updated.

    @param:
        request - contains metadata about the requested page.

    @variables:
        from_date - The starting date for the academic calendar event.
        to_date - The ending date for the academic caldendar event.
        desc - Description for the academic calendar event.
        prev_desc - Description for the previous event which is to be updated.
        c = object to save new event to the academic calendar.
        get_calendar_details = Get the object of the calendar instance from the database for the previous Description.

    """
    calendar = Calendar.objects.all()
    context= {
        'academic_calendar' :calendar,
        'tab_id' :['4','1']
    }
    if request.method == "POST":
        print("Requested Method: ", request.POST)
        from_date = request.POST.getlist('from_date')
        to_date = request.POST.getlist('to_date')
        desc = request.POST.getlist('description')[0]
        prev_desc = request.POST.getlist('prev_desc')[0]
        print(from_date, to_date, desc, prev_desc)
        from_date = from_date[0].split('-')
        from_date = [int(i) for i in from_date]
        from_date = datetime.datetime(*from_date).date()
        to_date = to_date[0].split('-')
        to_date = [int(i) for i in to_date]
        to_date = datetime.datetime(*to_date).date()
        get_calendar_details = Calendar.objects.all().filter(description=prev_desc).first()
        get_calendar_details.description = desc
        get_calendar_details.from_date = from_date
        get_calendar_details.to_date = to_date
        get_calendar_details.save()
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


#Generate Attendance Sheet
def sem_for_generate_sheet():
    """
    This function generates semester grade sheet
    @variables:
        now - current datetime
        month - current month
    """
    now = datetime.datetime.now()
    month = int(now.month)
    if month >= 7 and month <= 12:
        return [1, 3, 5, 7]
    else:
        return [2, 4, 6, 8]


def generatexlsheet(request):
    """
    to generate Course List of Registered Students

    @param:
        request - contains metadata about the requested page

    @variables:
        f_key - gets the courses
        idd - Dictionary value of post data year
        course_id - Course object according to idd
        obj - Registration object of the year in idd
        ans - Formatted Array to be converted to xlsx
        k -temporary array to add data to formatted array/variable
        output - io Bytes object to write to xlsx file
        book - workbook of xlsx file
        title - formatting variable of title the workbook
        subtitle - formatting variable of subtitle the workbook
        normaltext - formatting variable for normal text
        sheet - xlsx sheet to be rendered
        titletext - formatting variable of title text
        dep - temporary variables
        z - temporary variables for final output
        b - temporary variables for final output
        c - temporary variables for final output
        st - temporary variables for final output
    """
    print(request.POST)
    batch = request.POST['batch']
    course = Course.objects.get(course_name=request.POST['course'])
    curr_key = Curriculum.objects.filter(course_id = course).filter(batch=batch).first()
    obj = Register.objects.all().filter(curr_id = curr_key).filter(year=batch)
    ans = []
    print(obj)
    for i in obj:
        k = []
        k.append(i.student_id.id.id)
        k.append(i.student_id.id.user.first_name)
        k.append(i.student_id.id.user.last_name)
        k.append(i.student_id.id.department)
        ans.append(k)
    ans.sort()
    output = BytesIO()

    book = Workbook(output,{'in_memory':True})
    title = book.add_format({'bold': True,
                                'font_size': 22,
                                'align': 'center',
                                'valign': 'vcenter'})
    subtitle = book.add_format({'bold': True,
                                'font_size': 15,
                                'align': 'center',
                                'valign': 'vcenter'})
    normaltext = book.add_format({'bold': False,
                                'font_size': 15,
                                'align': 'center',
                                'valign': 'vcenter'})
    sheet = book.add_worksheet()

    title_text = ((str(course.course_name)+" : "+str(str(batch))))
    #width = len(title_text)
    sheet.set_default_row(25)

    sheet.merge_range('A2:E2', title_text, title)
    sheet.write_string('A3',"Sl. No",subtitle)
    sheet.write_string('B3',"Roll No",subtitle)
    sheet.write_string('C3',"Name",subtitle)
    sheet.write_string('D3',"Discipline",subtitle)
    sheet.write_string('E3','Signature',subtitle)
    sheet.set_column('A:A',20)
    sheet.set_column('B:B',20)
    sheet.set_column('C:C',60)
    sheet.set_column('D:D',15)
    sheet.set_column('E:E',30)
    k = 4
    num = 1
    for i in ans:
        sheet.write_number('A'+str(k),num,normaltext)
        num+=1
        z,b,c = str(i[0]),i[1],i[2]
        name = str(b)+" "+str(c)
        temp = str(i[3]).split()
        dep = str(temp[len(temp)-1])
        sheet.write_string('B'+str(k),z,normaltext)
        sheet.write_string('C'+str(k),name,normaltext)
        sheet.write_string('D'+str(k),dep,normaltext)
        k+=1
    book.close()
    output.seek(0)
    response = HttpResponse(output.read(),content_type = 'application/vnd.ms-excel')
    st = 'attachment; filename = ' + curr_key.course_code + '.xlsx'
    response['Content-Disposition'] = st
    return response


def generate_preregistration_report(request):
    """
    to generate preresgistration report after pre-registration

    @param:
        request - contains metadata about the requested page

    @variables:
        sem - rollno of the student to become the senator
        obj1 - All the registration details of 1st years
        obj2 - All the registration details of 2nd years
        obj3 - All the registration details of 3rd years
        obj4 - All the registration details of 4th years
        obj - All the registration details appended into one
        data - Formated data for context
        m - counter for Sl. No (in formated data)
        z - temporary array to add data to variable data

    """
    if request.method == "POST":
        print(request.POST)    
        sem = sem_for_generate_sheet()
        print(sem)
        now = datetime.datetime.now()
        year = int(now.year)
        batch=request.POST['batch']
        if sem[0] == 2:
            sem = sem[year-int(batch)-1]
        else:
            sem = sem[year-int(batch)]
        sem+=1
        sem=6
        print(sem)
        obj = InitialRegistrations.objects.filter(batch=batch).filter(semester=sem)
        print(obj)
        data = []
        m = 1
        for i in obj:
            z = []
            z.append(m)
            m += 1
            z.append(i.student_id.id.user.username)
            z.append(str(i.student_id.id.user.first_name)+" "+str(i.student_id.id.user.last_name))
            z.append(i.student_id.id.department.name)
            z.append(i.curr_id.credits)
            z.append(i.curr_id.course_code)
            z.append(i.curr_id.course_id)
            data.append(z)
        data.sort()
        output = BytesIO()

        book = Workbook(output,{'in_memory':True})
        title = book.add_format({'bold': True,
                                    'font_size': 22,
                                    'align': 'center',
                                    'valign': 'vcenter'})
        subtitle = book.add_format({'bold': True,
                                    'font_size': 15,
                                    'align': 'center',
                                    'valign': 'vcenter'})
        normaltext = book.add_format({'bold': False,
                                    'font_size': 15,
                                    'align': 'center',
                                    'valign': 'vcenter'})
        sheet = book.add_worksheet()

        title_text = (("Pre-registeration : Batch - "+str(str(batch))))
        #width = len(title_text)
        sheet.set_default_row(25)

        sheet.merge_range('A2:E2', title_text, title)
        sheet.write_string('A3',"Sl. No",subtitle)
        sheet.write_string('B3',"Roll No",subtitle)
        sheet.write_string('C3',"Name",subtitle)
        sheet.write_string('D3',"Discipline",subtitle)
        sheet.write_string('E3','Credits',subtitle)
        sheet.write_string('F3','Course Code',subtitle)
        sheet.write_string('G3','Course Name',subtitle)
        sheet.write_string('H3','Signature',subtitle)
        sheet.set_column('A:A',20)
        sheet.set_column('B:B',20)
        sheet.set_column('C:C',50)
        sheet.set_column('D:D',15)
        sheet.set_column('E:E',15)
        sheet.set_column('F:F',20)
        sheet.set_column('G:G',60)
        sheet.set_column('H:H',15)
        k = 4
        num = 1
        for i in data:
            sheet.write_number('A'+str(k),num,normaltext)
            num+=1
            print(i)
            z,b,c = str(i[0]),i[1],i[2]
            a,b,c,d,e,f,g = str(i[0]),str(i[1]),str(i[2]),str(i[3]),str(i[4]),str(i[5]),str(i[6])
            name = str(b)+" "+str(c)
            temp = str(i[3]).split()
            dep = str(temp[len(temp)-1])
            sheet.write_string('B'+str(k),b,normaltext)
            sheet.write_string('C'+str(k),c,normaltext)
            sheet.write_string('D'+str(k),d,normaltext)
            sheet.write_string('E'+str(k),e,normaltext)
            sheet.write_string('F'+str(k),f,normaltext)
            sheet.write_string('G'+str(k),g,normaltext)
            k+=1
        book.close()
        output.seek(0)
        response = HttpResponse(output.read(),content_type = 'application/vnd.ms-excel')
        st = 'attachment; filename = ' + str(batch) + '-preresgistration.xlsx'
        response['Content-Disposition'] = st
        return response


def add_new_profile(request):
    context= {
        'tab_id' :['2','1']
    }
    if request.method == 'POST' and request.FILES:
        profiles=request.FILES['profiles']
        print (profiles)
        excel = xlrd.open_workbook(file_contents=profiles.read())
        sheet=excel.sheet_by_index(0)
        for i in range(1,sheet.nrows):
            roll_no=int(sheet.cell(i,0).value)
            first_name=str(sheet.cell(i,1).value)
            last_name=str(sheet.cell(i,2).value)
            email=str(sheet.cell(i,3).value)
            sex=str(sheet.cell(i,4).value)
            if sex is 'F':
                title='Ms.'
            else:
                title='Mr.'
            dob_tmp=sheet.cell(i,5).value
            dob=datetime.datetime(*xlrd.xldate_as_tuple(dob_tmp,excel.datemode))
            fathers_name=str(sheet.cell(i,6).value)
            mothers_name=str(sheet.cell(i,7).value)
            category=str(sheet.cell(i,8).value)
            phone_no=int(sheet.cell(i,9).value)
            address=str(sheet.cell(i,10).value)
            dept=str(sheet.cell(i,11).value)
            department=DepartmentInfo.objects.get(name=dept)
            specialization=str(sheet.cell(i,12).value)
            if specialization is "":
                specialization="None"
            hall_no=sheet.cell(i,13 ).value
            if hall_no is "":
                hall_no=3
            else:
                hall_no=int(hall_no)
            programme=request.POST['Programme']
            batch=request.POST['Batch']

            user = User.objects.create_user(
                username=roll_no,
                password='hello123',
                first_name=first_name,
                last_name=last_name,
                email=email,
            )

            einfo = ExtraInfo.objects.create(
                id=roll_no,
                user=user,
                title=title,
                sex=sex,
                date_of_birth=dob,
                address=address,
                phone_no=phone_no,
                user_type='student',
                department=department,
            )

            stud_data = Student.objects.create(
                id=einfo,
                programme=programme,
                batch=batch,
                cpi=0,
                category=category,
                father_name=fathers_name,
                mother_name=mothers_name,
                hall_no=hall_no,
                specialization=specialization,
            )

            desig = Designation.objects.get(name='student')
            hold_des = HoldsDesignation.objects.create(
                user=user,
                working=user,
                designation=desig,
            )
            
            # print(roll_no)
            # print(first_name)
            # print(last_name)
            # print(email)
            # print(sex)
            # print(dob)
            # print(fathers_name)
            # print(mothers_name)
            # print(category)
            # print(phone_no)
            # print(address)
            # print(programme)
            # print(dept)
            # print(specialization)
            # print(hall_no)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def get_faculty_list():
    f1 = HoldsDesignation.objects.filter(designation=Designation.objects.get(name = "Assistant Professor"))
    f2 = HoldsDesignation.objects.filter(designation=Designation.objects.get(name = "Professor"))
    f3 = HoldsDesignation.objects.filter(designation=Designation.objects.get(name = "Associate Professor"))

    faculty = list(chain(f1,f2,f3))
    faculty_list = []
    for i in faculty:
        faculty_list.append(i)
    return faculty_list


def float_course(request):
    context= {
        'tab_id' :['5','1']
    }
    if request.method == 'POST':
        print("float_course")
        print(request.POST)
        try:
            request_batch = request.POST['batch']
            request_branch = request.POST['branch']
            request_programme = request.POST['programme']
        except:
            request_batch = ""
            request_branch = ""
            request_programme = ""

        if request_batch == "" and request_branch == "" and request_programme=="":
            curriculum = None   #Curriculum.objects.all()
        else:
            sem = sem_for_generate_sheet()
            print(sem)
            now = datetime.datetime.now()
            year = int(now.year)
            # if sem[0] == 2:
            #     sem = sem[year-int(request_batch)-1]
            # else:
            #     sem = sem[year-int(request_batch)]
            # sem+=1
            sem=2
            print(request_branch,end=" ")
            print(request_batch,end=" ")
            print(request_programme)
            curriculum = Curriculum.objects.filter(branch = request_branch).filter(batch = request_batch).filter(programme= request_programme).filter(sem=sem).order_by('course_code')
        faculty_list = get_faculty_list()
        courses = Course.objects.all()
        course_type = Constants.COURSE_TYPE
        print(curriculum)
        context= {
            'courses': courses,
            'course_type': course_type,
            'curriculum': curriculum,
            'faculty_list': faculty_list,
            'tab_id' :['5','1']
        }
        return render(request, "ais/ais.html", context)
    else:
        return render(request, "ais/ais.html", context)
    return render(request, "ais/ais.html", context)


def float_course_submit(request):
    context= {
        'tab_id' :['5','1']
    }
    if request.method == "POST":
        print("float_course_submit")
        print(request.POST)
        i=1
        print (str(i)+"_ccode")
        while True:
            if str(i)+"_ccode" in request.POST:
                if str(i)+"_fac" in request.POST:
                    if request.POST[str(i)+"_fac"] == "" :
                        print("No faculty")
                    else:
                        print(request.POST[str(i)+"_fac"],end=" ")
                        flot = Curriculum.objects.get(curriculum_id=request.POST[str(i)+"_ccode"])
                        flot.floated = True
                        flot.save()
                        inst = get_object_or_404(User, username = request.POST.get(str(i)+"_fac"))
                        inst = ExtraInfo.objects.get(user=inst)
                        Curriculum_Instructor.objects.create(
                            curriculum_id=flot,
                            instructor_id=inst,
                        )
                        print("121212")
                print (request.POST[str(i)+"_ccode"])
            else:
                print("break")
                break
            i+=1
    return render(request, "ais/ais.html", context)












# # ---------------------senator------------------
# @csrf_exempt
def senator(request):
#     """
#     to add a new student senator

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - gets the data of current user.
#         user_details - gets the details of the required user.
#         desig_id - used to check the designation ID.
#         extraInfo - extraInfo object of the student with that rollno
#         s - designation object of senator
#         hDes - holdsDesignation object to store that the particualr student is holding the senator designation
#         student - the student object of the new senator
#         data - data of the student to be displayed in teh webpage

#     """
#     current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
    temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
    print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     if request.method == 'POST':
#         print(request.POST, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
#         rollno = request.POST.getlist('Roll Number')[0]
#         # print(request.POST.get('rollno'))
#         extraInfo = ExtraInfo.objects.get(id=rollno)
#         s = Designation.objects.get(name='Senator')
#         hDes = HoldsDesignation()
#         hDes.user = extraInfo.user
#         hDes.working = extraInfo.user
#         hDes.designation = s
#         hDes.save()
#         student = Student.objects.get(id=extraInfo)
#         data = {
#             'name': extraInfo.user.username,
#             'rollno': extraInfo.id,
#             'programme': student.programme,
#             'branch': extraInfo.department.name
#         }
#         return HttpResponseRedirect('/aims/')
#         # return JsonResponse(data)
#     else:
#         return HttpResponseRedirect('/aims/')

# @csrf_exempt
def deleteSenator(request, pk):
#     """
#     to remove a senator from the position

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         s - the designation object that contains senator
#         student - the list students that is a senator
#         hDes - the holdDesignation object that stores the
#                information that the particular student is a senator

#     """
    print(request.POST)
#     if request.POST:
#         s = get_object_or_404(Designation, name="Senator")
#         student = get_object_or_404(ExtraInfo, id=request.POST.getlist("senate_id")[0])
#         hDes = get_object_or_404( HoldsDesignation, user = student.user)
#         hDes.delete()
#         return HttpResponseRedirect('/aims/')
#     else:
#         return HttpResponseRedirect('/aims/')# ####################################################


# # ##########covenors and coconvenors##################
# @csrf_exempt
def add_convenor(request):
#     """
#     to add a new student convenor/coconvenor

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         rollno - rollno of the student to become the convenor/coconvenor
#         extraInfo - extraInfo object of the student with that rollno
#         s - designation object of Convenor
#         p - designation object of Co Convenor
#         result - the data that contains where the student will become
#                  convenor or coconvenor
#         hDes - holdsDesignation object to store that the particualr student is
#                holding the convenor/coconvenor designation
#         student - the student object of the new convenor/coconvenor
#         data - data of the student to be displayed in the webpage

#     """
    s = Designation.objects.get(name='Convenor')
#     p = Designation.objects.get(name='Co Convenor')
#     if request.method == 'POST':
#         rollno = request.POST.get('rollno_convenor')
#         extraInfo = ExtraInfo.objects.get(id=rollno)
#         s = Designation.objects.get(name='Convenor')
#         p = Designation.objects.get(name='Co Convenor')
#         result = request.POST.get('designation')
#         hDes = HoldsDesignation()
#         hDes.user = extraInfo.user
#         hDes.working = extraInfo.user
#         if result == "Convenor":
#             hDes.designation = s
#         else:
#             hDes.designation = p
#         hDes.save()
#         data = {
#             'name': extraInfo.user.username,
#             'rollno_convenor': extraInfo.id,
#             'designation': hDes.designation.name,
#         }
#         return JsonResponse(data)
#     else:
#         data = {}
#         return JsonResponse(data)

# @csrf_exempt
def deleteConvenor(request, pk):
#     """
#     to remove a convenor/coconvenor from the position

#     @param:
#         request - contains metadata about the requested page
#         pk - the primary key of that particular student field

#     @variables:
#         s - the designation object that contains convenor
#         c - the designation object that contains co convenor
#         student - the student object with the given pk
#         hDes - the holdDesignation object that stores the
#                information that the particular student is a convenor/coconvenor to be deleted
#         data - data of the student to be hidden in the webpage

#     """
#     s = get_object_or_404(Designation, name="Convenor")
    c = get_object_or_404(Designation, name="Co Convenor")
#     student = get_object_or_404(ExtraInfo, id=pk)
#     hDes = HoldsDesignation.objects.filter(user = student.user)
#     designation = []
#     for des in hDes:
#         if des.designation == s or des.designation == c:
#             designation = des.designation.name
#             des.delete()
#     data = {
#         'id': pk,
#         'designation': designation,
#     }
#     return JsonResponse(data)# ######################################################


# # ##########Senate meeting Minute##################
# @csrf_exempt
def addMinute(request):
#     """
#     to add a new senate meeting minute object to the database.

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - details of the current user.
#         desig_id - to check the designation of the user.
#         user_details - to get the details of the required user.

#     """
#     current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
    temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     if request.method == 'POST' and request.FILES:
#         form = MinuteForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponse('sucess')
#         else:
#             return HttpResponse('not uploaded')
#         return render(request, "ais/ais.html", {})


def deleteMinute(request):
#     """
#     to delete an existing senate meeting minute object from the database.

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         data - the id of the minute object to be deleted
#         t - the minute object received from id to be deleted

#     """
#     if request.method == "POST":
#         data = request.POST['delete']
#         t = Meeting.objects.get(id=data)
#         t.delete()

    return HttpResponseRedirect('/aims/')
# # ######################################################


# # ##########Student basic profile##################
# @csrf_exempt
def add_basic_profile(request):
#     """
#     It adds the basic profile information like username,password, name,
#     rollno, etc of a student

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         name - the name of the student
#         roll - the rollno of the student
#         batch - the current batch of the student
#         programme - the programme the student is enrolled in
#         ph - the phone number of the student

#     """
    if request.method == "POST":
        name = request.POST.get('name')
#         roll = ExtraInfo.objects.get(id=request.POST.get('rollno'))
#         programme = request.POST.get('programme')
#         batch = request.POST.get('batch')
#         ph = request.POST.get('phoneno')
#         if not Student.objects.filter(id=roll).exists():
#             db = Student()
#             st = ExtraInfo.objects.get(id=roll.id)
#             db.name = name.upper()
#             db.id = roll
#             db.batch = batch
#             db.programme = programme
#             st.phone_no = ph
#             db.save()
#             st.save()
#             data = {
#                 'name': name,
#                 'rollno': roll.id,
#                 'programme': programme,
#                 'phoneno': ph,
#                 'batch': batch
#             }
#             print(data)
#             return JsonResponse(data)
#         else:
#             data = {}
#             return JsonResponse(data)
#     else:
#         data = {}
#         return JsonResponse(data)


# @csrf_exempt
def delete_basic_profile(request, pk):
#     """
#     Deletes the student from the database

#     @param:
#         request - contains metadata about the requested page
#         pk - the primary key of the student's record in the database table

#     @variables:
#         e - the extraInfo objects of the student
#         user - the User object of the student
#         s - the student object of the student

#     """
    e = get_object_or_404(ExtraInfo, id=pk)
#     user = get_object_or_404(User, username = e.user.username)
#     s = get_object_or_404(Student, id=e)
#     data = {
#         'rollno': pk,
#     }
#     s.delete()
#     e.delete()
#     u.delete()
#     return JsonResponse(data)# #########################################################

# '''
# # view to add attendance data to database
# def curriculum(request):

# '''





def add_attendance(request):
#     """
#     to add/edit a student attendance to the database

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - details of the current user.
#         user_details - details of the required user.
#         desig_id - to check the dwsignation of the user.
#         course_id - the course id of the course for attendance entry from the user
#         rollno - the rollno of the particular student
#         total - the total no. of class
#         attended - no of class attended by the student
#         c_id - the course object from the course id
#         s_id - the student object retrieved from the rollno
#         check - checking whether data is already available. if true, it is overwritten
#         form - if not, a new addendance object field is created in the databse

#     """
    current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     if request.method == 'POST':

#         course_id = request.POST.getlist('course_id')[0]
#         rollno = request.POST.getlist('rollno')[0]
#         total = int(request.POST.get('Total'))
#         attended = int(request.POST.get('attended'))

#         c_id = Course.objects.get(course_id=course_id)
#         s_id = ExtraInfo.objects.get(id=rollno)
#         s_id = Student.objects.get(id=s_id)
#         check = Student_attendance.objects.all().filter(course_id=c_id, student_id=s_id).first()
#         if (check):
#             check.total_attend = total
#             check.present_attend = attended
#             check.save()
#         else:
#             form = Student_attendance(
#                 student_id = s_id,
#                 course_id= c_id,
#                 present_attend = attended,
#                 total_attend = total
#             )
#             form.save()
#         context['result'] = 'Success'
#         return HttpResponse(json.dumps(context), content_type='delete_attendance/json')
#     return HttpResponse('/aims/')

# # view to fetch attendance data
def get_attendance(request):
#     """
#     to fetch existing attendance list of a particular course and student from the database

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - the username of the logged in user
#         user_details - the details of the current user
#         desig_id - checking the designation of the current user
#         acadadmin - deatils of the acad admin
#         course_id - the attendance of which course we are taking
#         stud_data - the data of the student

#     """
#     current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
    desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     course_id = request.GET.get('course_id')

#     c_id = Course.objects.get(course_id=course_id)
#     data = Student_attendance.objects.filter(course_id_id=c_id).values_list('course_id_id',
#                                                                             'student_id_id',
#                                                                             'present_attend',
#                                                                             'total_attend')
#     stud_data = {}
#     stud_data['name'] = []
#     stud_data['programme'] = []
#     stud_data['batch'] = []
#     for obj in data:
#         roll = obj[1]
#         extra_info = ExtraInfo.objects.get(id=roll)
#         s_id = Student.objects.get(id=extra_info)

#         stud_data['name'].append(s_id.name)
#         stud_data['programme'].append(s_id.programme)
#         stud_data['batch'].append(s_id.batch)

#     context = {}
#     try:
#         context['result'] = 'Success'
#         context['tuples'] = list(data)
#         context['stud_data'] = stud_data
#     except:
#         context['result'] = 'Failure'

#     return HttpResponse(json.dumps(context), content_type='get_attendance/json')


# # view to delete attendance data
def delete_attendance(request):
#     """
#     to delete the attendance of a particular student and course

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - the username of the logged in user
#         user_details - the details of the current user
#         desig_id - checking the designation of the current user
#         acadadmin - deatils of the acad admin
#         course_id - the attendance of which course we are taking
#         student_id - the id of the student object
#         student_attend - the attendance object of the particular student

#     """
    current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     course_id = request.GET.get('course_id')
#     student_id = request.GET.get('student_id')
#     c_id = Course.objects.get(course_id=course_id)
#     student_attend = Student_attendance.objects.get(student_id_id=student_id, course_id_id=c_id)
#     student_attend.delete()
#     context = {}
#     context['result'] = 'Success'
#     return HttpResponse(json.dumps(context), content_type='delete_attendance/json')


def delete_advanced_profile(request):
#     """
#     to delete the advance information of the student

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - the username of the logged in user
#         user_details - the details of the current user
#         desig_id - checking the designation of the current user
#         acadadmin - deatils of the acad admin
#         s - the student object from the requested rollno

#     """
    current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     if request.method == "POST":
#         st = request.POST['delete']
#         arr = st.split("-")
#         stu = arr[0]
#         if Student.objects.get(id=stu):
#             s = Student.objects.get(id=stu)
#             s.father_name = ""
#             s.mother_name = ""
#             s.hall_no = 1
#             s.room_no = ""
#             s.save()
#         else:
#             return HttpResponse("Data Does Not Exist")

#     return HttpResponse("Data Deleted Successfully")


def add_advanced_profile(request):
#     """
#     It adds the advance profile information like hall no, room no,
#     profile picture, about me etc of a student

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - the username of the logged in user
#         user_details - the details of the current user
#         desig_id - checking the designation of the current user
#         acadadmin - deatils of the acad admin
#         father - father's name of the student
#         rollno - the rollno of the student required to check if the student is available
#         mother - mother's name of the student
#         add - student's address
#         cpi - student's cpi
#         hall - hall no of where the student stays
#         room no - hostel room no

#     """
    current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     if request.method == "POST":
#         print(request.POST)
#         rollno=request.POST.get('roll')
#         print(rollno)
#         student = ExtraInfo.objects.get(id=rollno)
#         print(student.address)
#         if not student:
#             data = {}
#             return JsonResponse(data)
#         else:
#             father = request.POST.get('father')
#             mother = request.POST.get('mother')
#             add = request.POST.get('address')
#             hall = request.POST.get('hall')
#             room = request.POST.get('room')
#             cpi = request.POST.get('cpi')
#             student.address = str(hall) + " " + str(room)
#             student.save()
#             s = Student.objects.get(id=student)
#             s.father_name=father
#             s.mother_name=mother
#             s.hall_no = hall
#             s.room_no = room
#             s.save()

#             return HttpResponseRedirect('/academic-procedures/')
#     return HttpResponseRedirect('/academic-procedures/')


def add_optional(request):
#     """
#     acadmic admin to update the additional courses

#     @param:
#         request - contains metadata about the requested page.

#     @variables:
#         choices - selected addtional courses by the academic person.
#         course - Course details which is selected by the academic admin.
#     """
    if request.method == "POST":
        print(request.POST)
#         choices = request.POST.getlist('choice')
#         for i in choices:
#             course = Course.objects.all().filter(course_id=i).first()
#             course.acad_selection = True
#             course.save()
#         courses = Course.objects.all()
#         for i in courses:
#             if i.course_id not in choices:
#                 i.acad_selection = False
#                 i.save()
#         return HttpResponseRedirect('/academic-procedures/')


def min_cred(request):
#     """
#     to set minimum credit for a current semester that a student must take

#     @param:
#         request - contains metadata about the requested page.

#     @variables:
#         sem_cred = Get credit details from forms and the append it to an array.
#         sem - Get the object for the minimum credits from the database and the update it.
#     """
    if request.method=="POST":
        sem_cred = []
#         sem_cred.append(0)
#         for i in range(1, 10):
#             sem = "sem_"+"1"
#             sem_cred.append(request.POST.getlist(sem)[0])

#         for i in range(1, 9):
#             sem = MinimumCredits.objects.all().filter(semester=i).first()
#             sem.credits = sem_cred[i+1]
#             sem.save()
#         return HttpResponse("Worked")


def view_course(request):
#     if request.method == "POST":
#         programme=request.POST['programme']
#         batch=request.POST['batch']
#         branch=request.POST['branch']
#         sem=request.POST['sem']

#         curriculum_courses = Curriculum.objects.filter(branch = branch).filter(batch = batch).filter(programme= programme).filter(sem = sem)
#         print(curriculum_courses)
#         courses = Course.objects.all()
#         course_type = Constants.COURSE_TYPE
#         context= {
#             'courses': courses,
#             'course_type': course_type,
#             'curriculum_course': curriculum_courses,
#         }
#         return render(request, "ais/ais.html", context)
#     else:
#         return render(request, "ais/ais.html")
    return render(request, "ais/ais.html")
    


def delete_grade(request):
#     """
#     It deletes the grade of the student

#     @param:
#         request - contains metadata about the requested page

#     @variables:
#         current_user - father's name of the student
#         user_details - the rollno of the student required to check if the student is available
#         desig_id - mother 's name of the student
#         acadadmin - student's address
#         final_user - details of the user
#         sem - current semester of the student
#         data - tag whether to delete it or not
#         course - get the course details
#     """
#     current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     print(request.POST['delete'])
#     data = request.POST['delete']
#     d = data.split("-")
#     id = d[0]
#     course = d[2]
#     sem = int(d[3])
#     if request.method == "POST":
#         if(Grades.objects.filter(student_id=id, sem=sem)):
#             s = Grades.objects.filter(student_id=id, sem=sem)
#             for p in s:
#                 if (str(p.course_id) == course):
#                     print(p.course_id)
#                     p.delete()
#         else:
#             return HttpResponse("Unable to delete data")
    return HttpResponse("Data Deleted SuccessFully")


def add_course(request):
#     """
#     to add a course to the database

#     @param:
#         request - contains metadata about the requested page.

#     @variables:
#         current_user - the username of the logged in user
#         user_details - the details of the current user
#         desig_id - checking the designation of the current user
#         acadadmin - deatils of the acad admin
#         c_id = course id to be added to the database.
#         c_name = course name to be added to the database.
#         c_opt = check if the course is optional or not.
#         c_sem = The semester for which the course belong.
#         c_cred = The credit of the course to be added to the database.
#         c_check = Check whether optional of subject is true or not.
#         c_save = Save a course instance to the databse.

#     """
#     current_user = get_object_or_404(User, username=request.user.username)
#     user_details = ExtraInfo.objects.all().filter(user=current_user).first()
#     desig_id = Designation.objects.all().filter(name='Upper Division Clerk')
#     temp = HoldsDesignation.objects.all().filter(designation = desig_id).first()
#     print (temp)
#     print (current_user)
#     acadadmin = temp.working
#     k = str(user_details).split()
#     print(k)
#     final_user = k[2]

#     if (str(acadadmin) != str(final_user)):
#         return HttpResponseRedirect('/academic-procedures/')
#     if request.method == "POST":
#         try:
#             c = Student.objects.get(id=request.POST['roll'])
#         except:
#             return HttpResponse("Student Does Not Exist")
#         if(request.POST['c1']):
#             c_id = Course.objects.get(course_id=request.POST['c1'])
#             c.courses.add(c_id)
#         if(request.POST['c2']):
#             c_id2 = Course.objects.get(course_id=request.POST['c2'])
#             c.courses.add(c_id2)
#         if(request.POST['c3']):
#             c_id3 = Course.objects.get(course_id=request.POST['c3'])
#             c.courses.add(c_id3)
#         if(request.POST['c4']):
#             c_id4 = Course.objects.get(course_id=request.POST['c4'])
#             c.courses.add(c_id4)
#         if(request.POST['c5']):
#             c_id5 = Course.objects.get(course_id=request.POST['c5'])
#             c.courses.add(c_id5)
#         if(request.POST['c6']):
#             c_id6 = Course.objects.get(course_id=request.POST['c6'])
#             c.courses.add(c_id6)

#         c.save()
#         print(c.courses.all())
    return HttpResponse("Data Entered Successfully")