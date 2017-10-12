# -*- coding: utf-8 -*-
from django.conf.urls import url

from projects.views import ProjectsListView, ProjectDetailView, JoinProjectView, label_next_image, labels, label_view
from images.views import ImageLabelUpdateView

urlpatterns = [
    url(r'^$', ProjectsListView.as_view(), name='projects-list'),
    url(r'^(?P<slug>[-\w]+)/?$', ProjectDetailView.as_view(), name='porject-detail'),
    url(r'^(?P<slug>[-\w]+)/join/?$', JoinProjectView.as_view(), name='join-project'),
    url(r'^[-\w]+/image/(?P<pk>[0-9]+)/?$', ImageLabelUpdateView.as_view(), name='image-label-update'),
    url(r'^(?P<slug>[-\w]+)/next/$', label_next_image, name='label-next-image'),
    url(r'^(?P<slug>[-\w]+)/labels/$', labels, name='labels'),
    url(r'^label/(?P<labelid>[0-9]+)/$', label_view, name='label-view')
]
