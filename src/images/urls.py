# -*- coding: utf-8 -*-
from django.conf.urls import url
from images.views import upload_tar, export_labels


urlpatterns = [
    url(r'^(?P<projectid>[0-9]+)/upload-tar/$', upload_tar, name='upload-tar'),
    url(r'^(?P<projectid>[0-9]+)/export/$', export_labels, name='export-labels'),
]
