# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html

from projects.models import Label, Project, UsersProject


@python_2_unicode_compatible
class Image(models.Model):
    """
    Reference to a particular image file
    """

    image = models.ImageField()
    project = models.ForeignKey(Project)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '%s (%s)' % (self.image.name, self.project.slug)
    
    def preview(self):
        return format_html('<img src="{}">', self.image.url)


class ImageLabel(models.Model):
    """
    Link between image, its label and user who assigned it
    """
    
    image = models.ForeignKey(Image)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    label = models.ForeignKey(Label, blank=True, null=True)
    x1_coordinate = models.PositiveSmallIntegerField(null=True, blank=True)
    y1_coordinate = models.PositiveSmallIntegerField(null=True, blank=True)
    x2_coordinate = models.PositiveSmallIntegerField(null=True, blank=True)
    y2_coordinate = models.PositiveSmallIntegerField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    
    def get_absolute_url(self):
        return '/p/%s/image/%s' % (self.project.slug, self.pk)
    
    def __str__(self):
        return "%s - %s" % (self.user.username, self.image.image.name)
    
    def save(self, *args, **kwargs):
        """
        Override to update completed image counter
        """
        super(ImageLabel, self).save(*args, **kwargs)

        up = UsersProject.objects.get(user=self.user, project=self.project)
        up.completed_imgs += 1
        up.save()
