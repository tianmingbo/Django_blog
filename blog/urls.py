from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'(\w+)/article/(\d+)/$',views.article_detail),
]
