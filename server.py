# importe les modules importants
from pyexpat.errors import messages
import hug
import pronotepy
import datetime

# importe les ENT
from pronotepy.ent import *

# donne les infos sur l'user
@hug.get('/user')
def user(url, username, password, ent):
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))

    if client.logged_in:
        userData = {
            "name": client.info.name,
            "class": client.info.class_name,
            "establishment": client.info.establishment,
            "phone": client.info.phone,
            "profile_picture": client.info.profile_picture.url
        }

        return userData

## renvoie l'emploi du temps
@hug.get('/timetable')
def timetable(url, username, password, ent, dateString):
    dateToGet = datetime.datetime.strptime(dateString, "%Y-%m-%d")
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))

    if client.logged_in:
        lessons = client.lessons(dateToGet)

        lessonsData = []
        for lesson in lessons:
            lessonData = {
                "id": lesson.id,
                "subject": lesson.subject.name,
                "teacher": lesson.teacher_name,
                "room": lesson.classroom,
                "start": lesson.start.strftime("%Y-%m-%d %H:%M"),
                "end": lesson.end.strftime("%Y-%m-%d %H:%M"),
                "background_color": lesson.background_color,
                "status": lesson.status,
                "is_cancelled": lesson.canceled,
                "group_name": lesson.group_name,
            }
            lessonsData.append(lessonData)

        print(lessonsData)
        return lessonsData

## renvoie les devoirs
@hug.get('/homework')
def homework(url, username, password, ent, dateFrom, dateTo):
    dateFrom = datetime.datetime.strptime(dateFrom, "%Y-%m-%d").date()
    dateTo = datetime.datetime.strptime(dateTo, "%Y-%m-%d").date()
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))

    if client.logged_in:
        homeworks = client.homework(date_from=dateFrom, date_to=dateTo)

        homeworksData = []
        for homework in homeworks:
            files = []
            for file in homework.files:
                files.append({
                    "id": file.id,
                    "name": file.name,
                    "url": file.url
                })

            homeworkData = {
                "id": homework.id,
                "subject": homework.subject.name,
                "description": homework.description,
                "background_color": homework.background_color,
                "done": homework.done,
                "date": homework.date.strftime("%Y-%m-%d %H:%M"),
                "files": files
            }
            homeworksData.append(homeworkData)

        print(homeworksData)
        return homeworksData

## renvoie les notes
@hug.get('/grades')
def grades(url, username, password, ent):
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))
    allGrades = client.current_period.grades

    gradesData = []
    for grade in allGrades:
        gradeData = {
            "id": grade.id,
            "subject": grade.subject.name,
            "comments": grade.comments,
            "date": grade.date.strftime("%Y-%m-%d %H:%M"),
            "grade": {
                "value": grade.grade,
                "out_of": grade.out_of,
                "coefficient": grade.coefficient,
                "average": grade.average,
                "max": grade.max,
                "min": grade.min,
            }
        }

        gradesData.append(gradeReturn)

    averagesData = []

    allAverages = client.current_period.averages
    for average in allAverages:
        averageData = {
            "id": average.id,
            "subject": average.subject.name,
            "average": average.student,
            "class_average": average.class_averages,
            "max": average.max,
            "min": average.min,
            "out_of": average.out_of,
        }

        averagesData.append(averageData)

    gradeReturn = {
        "grades": gradesData,
        "averages": averagesData,
        "overall_average": client.current_period.overall_average,
    }

    return gradesData;

## renvoie les absences (NE FONCTIONNE PAS)
@hug.get('/absences')
def grades(url, username, password, ent):
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))
    allAbsences = client.current_period.absences

    absencesData = []
    for absence in allAbsences:
        absenceData = {
            "id": absence.id,
            "from": absence.from_date.strftime("%Y-%m-%d %H:%M"),
            "to": absence.to_date.strftime("%Y-%m-%d %H:%M"),
            "justified": absence.justified,
            "hours": absence.hours,
            "reasons": absence.reasons,
        }

        absencesData.append(absenceData)

    return absencesData;

@hug.get('/news')
def news(url, username, password, ent):
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))
    allNews = client.information_and_surveys()

    newsAllData = []
    for news in allNews:
        newsData = {
            "id": news.id,
            "title": news.title,
            "date": news.creation_date.strftime("%Y-%m-%d %H:%M"),
            "category": news.category,
            "survey": news.survey,
            "author": news.author,
            "content": news.content,
            "html_content": news._raw_content
        }

        newsAllData.append(newsData)

    return newsAllData;

@hug.get('/discussions')
def discussions(url, username, password, ent):
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))
    allDiscussions = client.discussions()

    discussionsAllData = []
    for discussion in allDiscussions:
        messages = []
        for message in discussion.messages:
            messages.append({
                "id": message.id,
                "content": message.content,
                "author": message.author,
                "date": message.date.strftime("%Y-%m-%d %H:%M"),
                "seen": message.seen,
            })

        discussionData = {
            "id": discussion.id,
            "subject": discussion.subject,
            "creator": discussion.creator,
            "date": discussion.creation_date.strftime("%Y-%m-%d %H:%M"),
            "messages": messages
        }

        discussionsAllData.append(discussionData)

    return discussionsAllData;

@hug.get('/export/ical')
def export_ical(url, username, password, ent):
    client = pronotepy.Client(url, username=username, password=password, ent=getattr(pronotepy.ent, ent))
    
    ical_url = client.export_ical()
    return ical_url

    