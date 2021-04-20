from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from PIL import Image
import geopy
from geopy.geocoders import Nominatim
from django.contrib.gis.geos import Point

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=200, null=True, blank=True)
    # befor we should install pip install pillow
    image = models.ImageField(default='default.jpg', upload_to = 'profile_pics')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    #for resizing the large profile images
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)




