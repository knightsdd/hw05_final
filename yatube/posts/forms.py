from django import forms

from . import models


class PostForm(forms.ModelForm):

    class Meta:
        model = models.Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):

    class Meta:
        model = models.Comment
        fields = ('text',)
