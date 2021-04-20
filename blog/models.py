from django.db import models
from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Profile
from PIL import Image
from django.urls import reverse
from django import forms
import geopy
from geopy.geocoders import Nominatim
from django.contrib.gis.geos import Point
from taggit.managers import TaggableManager

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    address = models.CharField(max_length=200, null=True, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete = models.CASCADE) # it means if user deleted we want to delete their posts as well
    tags = TaggableManager(help_text="A comma-separated list of tags.")

    def __str__(self): # this function is to printing the result when we query our table
        return self.title

    #find the location of specific post and redirects
    #user to post detail the user created
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk':self.pk})

    # it automatically populates the geom column after user posts an address from text address using geocoding (geopy)
    def save(self, *args, **kwargs):
        if self.address:
            self.geom = Point(Nominatim(user_agent="myGeocoder").geocode(self.address).longitude, Nominatim(user_agent="myGeocoder").geocode(self.address).latitude)
        super(Post, self).save(*args, **kwargs)
    

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    commenter_username = models.CharField(max_length=100)
    commenter_profile = models.ForeignKey(Profile, related_name='commenter_profile',on_delete=models.CASCADE,default=None, blank=True, null=True)
    commenter_profile_image = models.ImageField(default='default.jpg')
    comment = models.TextField(max_length=50)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "Comment on {}".format(str(self.date_posted))

class Like(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    liker_username = models.CharField(max_length=100)
    date_liked = models.DateTimeField(default=timezone.now)
    is_liked = models.BooleanField(db_index=True, default=True) 

    def __str__(self):
        return "Comment on {}".format(str(self.date_liked))