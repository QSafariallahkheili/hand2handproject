from django import forms 
from django.contrib.auth.models import User
from .models import Post, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 1, 'rows': 1}),
        }
        fields = ['comment']



