# -*- coding: utf-8 -*-
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.files import File
from django.shortcuts import get_object_or_404, render

from images.models import ImageLabel, Image
from projects.models import Label, UsersProject, Project


class ImageLabelUpdateView(LoginRequiredMixin, UpdateView):
    """
    Images to label should be assigned when an user joins a project.
    Thus now we just need to update labels for unlabeled images.
    """
    
    model = ImageLabel
    fields = ('label', )
    
    def next_unlabeled(self):
        """
        Returns PK of next unlabeled image or False if there is none.
        """
        
        npk = ImageLabel.objects.filter(user=self.request.user, label__isnull=True).exclude(pk=self.object.pk).first()
        return npk
    
    def get_object(self, *args, **kwargs):
        """
        User can only update his own labels.
        """
        
        obj = get_object_or_404(ImageLabel, pk=self.kwargs['pk'], user=self.request.user)
        return obj
    
    def get_success_url(self, *args, **kwargs):
        """
        If there are any unlabeled images, show the next one.
        """
        
        next_im = self.next_unlabeled()
        if next_im:
            return next_im.get_absolute_url()
        # FIXME: Replace with SUCCESS page
        return '/p/%s/' % self.object.project.slug
    
    def get_form(self, *args, **kwargs):
        """
        Limit label choices to current project only
        """
        form = super(ImageLabelUpdateView, self).get_form(*args, **kwargs)
        form.fields['label'].queryset = Label.objects.filter(project=self.object.project)
        return form
    
    def get_context_data(self, *args, **kwargs):
        """
        Model form does not contain help text thus we pass all info separately
        """
        context = super(ImageLabelUpdateView, self).get_context_data(*args, **kwargs)
        context['labels'] = Label.objects.filter(project=self.object.project)
        up = UsersProject.objects.get(user=self.request.user,
                                      project=self.object.project)
        context['progress'] = up.get_complete_percent()
        return context


def upload_tar(request, projectid):
    import tarfile

    if request.method == "POST":
        targzfile = request.FILES.get('tarfile', None)
        project = Project.objects.get(id=projectid)

        if tarfile:
            tar = tarfile.open(targzfile.temporary_file_path())
            tar.extractall()
            files = tar.getnames()
            tar.close()
            for image in files:
                i = Image(project=project)
                i.image.save(image, File(open(image, 'r')))
                i.save()

            return render(request, "images/upload_result.html", {
                "project": project,
                "files": files
            })


