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
        user = auth.authenticate(username=username, password=pwd)
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
    # 评论内容
    content_list = models.Comment.objects.filter(article_id=pk)
    print(content_list)
    # 最新文章
    new_articles = models.Article.objects.all()
    if len(new_articles) <= 4:
        return render(request, 'content.html', locals())
    else:
        new_articles = new_articles.reverse()
        new_articles = new_articles[0:4]
        return render(request, 'content.html', locals())


from django.db.models import F
import json


# 点赞或者踩
def up_or_down(request):
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get("is_up"))  # 获取点击，再转换格式
    user = request.user  # 谁点击的赞或cai
    response = {"state": True}
    try:
        models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
        models.Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
    except Exception as e:
        response['state'] = False
        response["first_action"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up
        # 获得已经提交的数据，避免重复提交
    return JsonResponse(response)


def comment(request):
    print(request.POST)
    content = request.POST.get("content")
    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    user_pk = request.user.pk
    response = {}
    if not pid:
        # 没有父评论
        comment_obj = models.Comment.objects.create(article_id=article_id, content=content, user_id=user_pk)
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, content=content, user_id=user_pk,
                                                    parent_comment_id=pid)
    response['create_time'] = comment_obj.create_time.strftime("%Y-%m-%d")
    response['content'] = comment_obj.content
    response['username'] = comment_obj.user.username

    return JsonResponse(response)


def comment_tree(request, article_id):
    ret = list(models.Comment.objects.filter(article_id=article_id).values('pk', 'content', 'parent_comment_id'))
    # print(ret)
    return JsonResponse(ret, safe=False)


def add_blog(request):
    if request.method == "POST":
        print(request.POST)
        title = request.POST.get('title')
        user = request.user
        article_content = request.POST.get('article_content')
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(article_content, "html.parse")
        desc = bs.text[0:150] + '...'
        # 过滤非法标签
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:
                tag.decompose()
        article_obj = models.Article.objects.create(user=user, tite=title, desc=desc)
        models.ArticleDetail.objects.create(content=str(bs), article=article_obj)

        return HttpResponse("添加成功")
    return render(request, 'add_blog.html', locals())
