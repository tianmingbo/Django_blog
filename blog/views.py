from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from blog import models, forms
from django.http import JsonResponse


# Create your views here.

def login(request):
    return render(request, 'login.html')


def index(request):
    if request.method == "POST":
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        print(username, pwd)
        print(models.UserInfo.objects.all())
        user = auth.authenticate(username=username, password=pwd)
        print(user)
        if user:
            auth.login(request, user)  # 在后端为该用户生成相关session数据
            return redirect('/index/')
        else:
            return redirect('/login/')
    articles = models.Article.objects.all()
    return render(request, 'index.html', locals())


def register(request):
    if request.method == "POST":
        ret = {'ret': 0, 'msg': ''}  # 设置返回信息
        use_form = forms.Register_Form(request.POST)  # 使用form组件进行检验
        if use_form.is_valid():
            # 如果检验通过，去数据库创建用户
            use_form.cleaned_data.pop('re_password')  # 去掉重复密码
            models.UserInfo.objects.create_user(**use_form.cleaned_data)
            ret['msg'] = '/index/'
            return JsonResponse(ret)
        else:
            ret['status'] = 1
            ret['msg'] = use_form.errors
            return JsonResponse(ret)
    use_form = forms.Register_Form()
    return render(request, 'register.html', locals())


def logout(request):
    auth.logout(request)
    return redirect("/index/")
