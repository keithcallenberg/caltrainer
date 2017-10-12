# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models import Count


@python_2_unicode_compatible
class Project(models.Model):
    """
    Image labeling project
    """

    slug = models.SlugField(unique=True, blank=True,
                            help_text="Will be provided automatically if left blank.")
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True,
                                   help_text="Can contain HTML. Will be placed inside a DIV element.")
    is_active = models.BooleanField(default=False,
                                    help_text="Enable project when it is ready for labeling.")
    train_count = models.IntegerField(verbose_name="Training image count",
                                      help_text="Number of images to show for a single user.",
                                      null=True,
                                      blank=True)
    created = models.DateTimeField(auto_now_add=True)
    annotated = models.BooleanField(default=False)
    users_can_add_labels = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        super(Project, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    

@python_2_unicode_compatible
class Label(models.Model):
    """
    Labels available in a project
    """

    text = models.CharField(max_length=50,
                            help_text="Short text shown as a choice.")
    code = models.CharField(max_length=20, blank=True,
                            help_text="Unique code representing this label.")
    description = models.TextField(blank=True,
                                   help_text="Longer description to explain meaning of label." +
                                             "Can contain HTML. Will be placed inside a DIV element.")
    project = models.ForeignKey(Project,
                                help_text="A project offering this label as a choice to user.")
    created_by = models.ForeignKey(User, null=True, blank=True)
    representative_image = models.ImageField(null=True, blank=True)
    
    class Meta:
        unique_together = ('code', 'project')
        
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.text)
        
        super(Label, self).save(*args, **kwargs)
    
    def __str__(self):
        if self.code:
            return "%s (%s - %s)" % (self.text, self.code, self.project.title)
        return "%s (%s)" % (self.text, self.project.title)

@python_2_unicode_compatible
class UsersProject(models.Model):
    """
    Links Users with Projects
    """
    
    completed_imgs = models.IntegerField(default=0,
        help_text="How many images have been labeled.")
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "%s - %s" % (self.user.username, self.project.title)
    
    def get_progress(self):
        if self.project.train_count is not None:
            percent = round((self.completed_imgs * 100.0) / self.project.train_count, 1)
            return (self.completed_imgs, self.project.train_count, percent)
        else:
            count = Project.objects.filter(id=self.project.id).aggregate(Count('image'))
            percent = round((self.completed_imgs * 100.0) / count['image__count'], 1)
            return (self.completed_imgs, count['image__count'], percent)
