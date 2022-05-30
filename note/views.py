from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from note.models import Note


def check_login(fn):
    def wrap(requset, *args, **kwargs):
        if 'username' not in requset.session or 'uid' not in requset.session:
            c_username = requset.COOKIES.get('username')
            c_uid = requset.COOKIES.get('uid')
            if not c_uid or not c_username:
                return HttpResponseRedirect('/user/login')
            else:
                requset.session['username'] = c_username
                requset.session['uid'] = c_uid
        return fn(requset, *args, **kwargs)
    return wrap

def list_view(request):
    #notes = Note.objects.all()
    notes = Note.objects.filter(is_active=True)
    return render(request, 'note/list_note.html', locals())

def update_note(request, note_id):
    try:
        note = Note.objects.get(id=note_id, is_active=True)
    except Exception as e:
        print('--update note error is %s'%(e))
        return HttpResponse('--the note is not existed!')

    if request.method == 'GET':

        return render(request, 'note/update_note.html', locals())
    elif request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        note.title = title
        note.content = content
        note.save()
        return HttpResponseRedirect('/note/all')

def delete_note(request):

    note_id = request.GET.get('note_id')
    if not note_id:
        return HttpResponse('--request error!')
    try:
        note = Note.objects.get(id=note_id,is_active=True)
    except Exception as e:
        print('--delete note get error %s'%(e))
        return HttpResponse('note id is error!')
    note.is_active = False
    note.save()

    return HttpResponseRedirect('/note/all')


@check_login
def add_view(request):


    if request.method == 'GET':
        return render(request, 'note/add_note.html')
    elif request.method == 'POST':
        uid = request.session['uid']
        title = request.POST['title']
        content = request.POST['content']

        Note.objects.create(title=title, content=content, user_id=uid)
        return HttpResponseRedirect('/note/all')
