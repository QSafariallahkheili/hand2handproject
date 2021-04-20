
# context_processor is used to send context variables to the template.html or base.html
# fro this a file with the name "context_processor.py" is created in app root directory
# and it is also must be registered in setting file
from django.contrib.auth.models import User
from .models import Post
from users.models import Profile

def add_variable_to_context(request):
    
    # to check if the user is logged in
    if request.user.is_authenticated:
        current_user = request.user
        #print(current_user.id)
        pro = Profile.objects.get(user_id = current_user.id)
        #print(pro.image.url)
        return {
            'userImage': pro.image.url
        }
    else:
        return {
            'imageUrl': 'test'
        }
