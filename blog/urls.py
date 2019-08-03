from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'(\w+)/article/(\d+)/$',views.article_detail),
    url(r'up_or_down/',views.up_or_down),
    url(r'comment/',views.comment),
    url(r'comment_tree/',views.comment_tree),
]
