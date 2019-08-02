from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from blog import models, forms
from django.http import JsonResponse
from django.db.models import Count


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


def article_detail(request, username, pk):
    '''
    :param request:
    :param username:  被访问的用户名
    :param pk:  #被访问的文章id
    :return:  #返回文章
    '''
    article_obj = models.Article.objects.filter(nid=pk).first()
    content = article_obj.articledetail.content
    # 获取username所写的文章，进行分类
    author_obj = models.UserInfo.objects.filter(username=username).first()
    articles = author_obj.article_set.all()  # 反向查询，获得所有文章
    arr = []
    for i in articles:
        arr.append(i.type)  # 获取文章的类型
    result = {}
    for i in set(arr):
        result[i] = arr.count(i)

    # 按时间分类
    archive_list = models.Article.objects.filter(user=author_obj).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")
    print(archive_list)

    # 最新文章
    new_articles = models.Article.objects.all()
    if len(new_articles) <= 4:
        return render(request, 'content.html', locals())
    else:
        new_articles = new_articles.reverse()
        new_articles = new_articles[0:4]
        return render(request, 'content.html', locals())
