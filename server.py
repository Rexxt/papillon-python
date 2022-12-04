# importe les modules importants
from pyexpat.errors import messages
import hug
import pronotepy
import datetime
import time
import secrets
import falcon

# importe les ENT
from pronotepy.ent import *

# système de tokens
saved_clients = {}
"""
saved_clients ->
    token ->
        client -> instance de pronotepy.Client
        last_interaction -> int (provenant de time.time(), entier représentant le temps depuis la dernière intéraction avec le client)
"""
client_timeout_threshold = 300 # le temps en sec avant qu'un jeton ne soit rendu invalide

def get_client(token: str) -> tuple[str, pronotepy.Client|None]:
    """Retourne le client Pronote associé au jeton.

    Args:
        token (str): le jeton à partir duquel retrouver le client.

    Returns:
        tuple: le couple (statut, client?) associé au jeton
            str: le statut de la demande ('ok' si le client est trouvé, 'expired' si le jeton a expiré, 'notfound' si le jeton n'est pas associé à un client)
            pronotepy.Client|None: une instance de client si le token est valide, None sinon.

    """
    if token in saved_clients:
        client_dict = saved_clients[token]
        if time.time() - client_dict['last_interaction'] < client_timeout_threshold:
            client_dict['last_interaction'] = time.time()
            return 'ok', client_dict['client']
        else:
            del saved_clients[token]
            print(len(saved_clients), 'valid tokens')
            return 'expired', None
    else:
        return 'notfound', None

# requête initiale :
# un client doit faire
# token = POST /generatetoken body={url, username, password, ent}
# GET * token=token
@hug.post('/generatetoken')
def generate_token(response, body=None):
    if not body is None:
        for rk in ('url', 'username', 'password', 'ent'):
            if not rk in body:
                response.status = falcon.get_http_status(400)
                return f'missing{rk}'
        client = pronotepy.Client(body['url'], username=body['username'], password=body['password'], ent=getattr(pronotepy.ent, body['ent']))
        token = secrets.token_urlsafe(16)

        saved_clients[token] = {
            'client': client,
            'last_interaction': time.time()
        }

        print(len(saved_clients), 'valid tokens')

        return token
    else:
        response.status = falcon.get_http_status(400)
        return 'missingbody'

# donne les infos sur l'user
@hug.get('/user')
def user(token, response):
    success, client = get_client(token)

    if success == 'ok':
        if client.logged_in:
            userData = {
                "name": client.info.name,
                "class": client.info.class_name,
                "establishment": client.info.establishment,
                "phone": client.info.phone,
                "profile_picture": client.info.profile_picture.url
            }

            return userData
    else:
        response.status = falcon.get_http_status(498)
        return success

## renvoie l'emploi du temps
@hug.get('/timetable')
def timetable(token, dateString, response):
    dateToGet = datetime.datetime.strptime(dateString, "%Y-%m-%d")
    success, client = get_client(token)

    if success == 'ok':
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
    else:
        response.status = falcon.get_http_status(498)
        return success

## renvoie les devoirs
@hug.get('/homework')
def homework(token, dateFrom, dateTo, response):
    dateFrom = datetime.datetime.strptime(dateFrom, "%Y-%m-%d").date()
    dateTo = datetime.datetime.strptime(dateTo, "%Y-%m-%d").date()
    success, client = get_client(token)

    if success == 'ok':
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

            return homeworksData
    else:
        response.status = falcon.get_http_status(498)
        return success

## renvoie les notes
@hug.get('/grades')
def grades(token, ent, response):
    success, client = get_client(token)
    if success == 'ok':
        allGrades = client.current_period.grades
        gradesData = []
        for grade in allGrades:
            gradeData = {
                "id": grade.id,
                "subject": grade.subject.name,
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

            gradesData.append(gradeData)

        averagesData = []

        allAverages = client.current_period.averages
        for average in allAverages:
            averageData = {
                "subject": average.subject.name,
                "average": average.student,
                "class_average": average.class_average,
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

        return gradeReturn
    else:
        response.status = falcon.get_http_status(498)
        return success

## renvoie les absences (NE FONCTIONNE PAS)
@hug.get('/absences')
def grades(token, response):
    success, client = get_client(token)
    if success == 'ok':
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

        return absencesData
    else:
        response.status = falcon.get_http_status(498)
        return success

@hug.get('/news')
def news(token, response):
    success, client = get_client(token)
    if success == 'ok':
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

        return newsAllData
    else:
        response.status = falcon.get_http_status(498)
        return success

@hug.get('/discussions')
def discussions(token, response):
    success, client = get_client(token)
    if success == 'ok':
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

        return discussionsAllData
    else:
        response.status = falcon.get_http_status(498)
        return success

@hug.get('/export/ical')
def export_ical(token, response):
    success, client = get_client(token)
    
    if success == 'ok':
        ical_url = client.export_ical()
        return ical_url
    else:
        response.status = falcon.get_http_status(498)
        return success

@hug.get('/homework/setAsDone')
def homework_setAsDone(token, dateFrom, dateTo, homeworkId, response):
    dateFrom = datetime.datetime.strptime(dateFrom, "%Y-%m-%d").date()
    dateTo = datetime.datetime.strptime(dateTo, "%Y-%m-%d").date()
    success, client = get_client(token)

    if success == 'ok':
        if client.logged_in:
            homeworks = client.homework(date_from=dateFrom, date_to=dateTo)

            incr = 0

            for homework in homeworks:
                if incr == homeworkId:
                    print(homework)
                    homework.set_done(False)

                incr += 1
    else:
        response.status = falcon.get_http_status(498)
        return success
    