from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^initialize/$', views.initialize, name='initialize'),
    url(r'^app/$', views.app, name='app'),
    url(r'^recipes/$', views.recipes, name='recipes')
]