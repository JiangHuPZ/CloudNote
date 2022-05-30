from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import User
import hashlib

# Create your views here.
def reg_view(request):
    # register
    if request.method == 'GET':
        return render(request, 'user/register.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']

        if password_1 != password_2:
            return HttpResponse('两次密码输入不一致')

        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()

        old_users = User.objects.filter(username=username)
        if old_users:
            return HttpResponse('用户名已经注册')
        # 处理并发写入
        try:
            user = User.objects.create(username=username, password=password_m)
        except Exception as e:
            print('--create user error %s'%(e))
            return HttpResponse('Username exited')
        # 免登录一天
        request.session['username'] = username
        request.session['uid'] = user.id

        return HttpResponseRedirect('/index')


def login_view(request):

    if request.method == 'GET':

        if request.session.get('username') and request.session.get('uid'):
            return HttpResponseRedirect('/index')


        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username and c_uid:
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            return HttpResponseRedirect('/index')

        return render(request, 'user/login.html')

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print('--login user error %s'%(e))
            return HttpResponse('username or password error')

        m = hashlib.md5()
        m.update(password.encode())
        if m.hexdigest() != user.password:
            return HttpResponse('username or password error')

        request.session['username'] = username
        request.session['uid'] = user.id
        resp = HttpResponseRedirect('/index')
        if 'remember' in request.POST:
            resp.set_cookie('username', username, 3600*24*3)
            resp.set_cookie('uid', user.id, 3600*24*3)

        return resp

def logout_view(request):
    resp = HttpResponseRedirect('/index')
    if request.session.get('username') and request.session.get('uid'):
        del request.session['username']
        del request.session['uid']
    if request.COOKIES.get('username') and request.COOKIES.get('uid'):
        resp.delete_cookie('username')
        resp.delete_cookie('uid')

    return resp