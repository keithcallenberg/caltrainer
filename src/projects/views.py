# -*- coding: utf-8 -*-
from random import randint

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import render

import json

from projects.models import Project, UsersProject, Label
from images.models import ImageLabel, Image


class ProjectsListView(ListView):
    model = Project
    order = ('is_active', 'created')


class ProjectDetailView(DetailView):
    model = Project
    
    def get_next(self, *args, **kwargs):
        """
        Returns URL of one of unlabeled images for particular user
        """
        
        if not self.request.user:
            return None
        
        im_pk = Image.objects.filter(project=self.object).exclude(imagelabel__user=self.request.user).values_list('id', flat=True).first()
        if im_pk:
            return '/p/%s/image/%s/' % (self.object.slug, im_pk)
        else:
            return None
    
    def get_usersproject(self):
        """
        Return userproject object for current user
        """
        if not self.request.user:
            return None
        
        up = UsersProject.objects.filter(user=self.request.user, project=self.object).first()
        return up


class JoinProjectView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/project_join.html'
    
    def post(self, request, *args, **kwargs):
        try:
            project = Project.objects.get(slug=kwargs['slug'])
        except Project.DoesNotExist:
            raise Http404("Project does not exist!")
        
        up = UsersProject.objects.filter(user=self.request.user, project=project).first()
        if up:
            return render(request, self.template_name, {
                'message': "You already have joined this project.",
                'project': project
            })
        
        up = UsersProject(user=self.request.user, project=project)
        up.save()
        
        return render(request, self.template_name, {
            'message': "You have joined the %s project!" % (project.title),
            'project': project
        })


def label_next_image(request, slug):
    project = Project.objects.get(slug=slug)

    if request.method == "POST" and request.is_ajax():
        json_object = {'success': False}
        image = Image.objects.get(id=request.POST.get('image'))
        annos = request.POST.get('annos', [])
        annos = json.loads(annos)
        for anno in annos:
            # look for label
            label = Label.objects.filter(text=anno['label'],
                                         project=project).first()
            if label is None:
                if project.users_can_add_labels:
                    label = Label(text=anno['label'],
                                  project=project,
                                  created_by=request.user)
                    label.save()
                else:
                    # TODO: might want to give some sort of warning here
                    continue

            ImageLabel.objects.create(label=label,
                                      image=image,
                                      user=request.user,
                                      project=project,
                                      x1_coordinate=anno['x1'],
                                      y1_coordinate=anno['y1'],
                                      x2_coordinate=anno['x2'],
                                      y2_coordinate=anno['y2'])

        json_object['success'] = True

        return JsonResponse(json_object)
    else:
        if request.method == "POST":
            # look for label
            label = Label.objects.filter(text=request.POST.get('label'),
                                         project=project).first()
            if label is None:
                if project.users_can_add_labels:
                    label = Label(text=request.POST.get('label'),
                                  project=project,
                                  created_by=request.user)
                else:
                    return Http404("Error: users cannot create labels for this project.")

            image = Image.objects.get(id=request.POST.get('image'))

            ImageLabel.objects.create(label=label,
                                      image=image,
                                      user=request.user,
                                      project=project)

        potential_images = Image.objects.filter(project=project).exclude(imagelabel__user=request.user)
        random_index = randint(0, potential_images.count() - 1)
        next_image = potential_images[random_index]
        labels = Label.objects.filter(project=project).order_by('text')
        progress = UsersProject.objects.get(user=request.user, project=project).get_progress()

    return render(request, "images/imagelabel_form.html", {
        "image": next_image,
        "project": project,
        "labels": labels,
        "progress": progress,
    })


def labels(request, slug):

    query = request.GET.get('source')

    project = Project.objects.get(slug=slug)
    labels = Label.objects.filter(project=project,
                                  text__icontains=query)

    topics = [{'id': x.id, 'title': x.text} for x in labels]

    response = {'detectedTopics': topics}

    return JsonResponse(response, safe=False)
