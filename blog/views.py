from django.shortcuts import render,get_object_or_404
from django.contrib.auth.mixins import (LoginRequiredMixin, # to create new post if user is not login direct them to login page
                                        UserPassesTestMixin, # to prevent users acess on updating other user's post and profile
)
from django.views.generic.edit import (FormMixin, # to combine form and detail view,
                                        ModelFormMixin
)
from django.contrib.auth.models import User
from users.models import Profile # importing Profile model from users app
from .models import Post, Comment, Like
from .forms import CommentForm
from django.views.generic import (ListView,
                                 DetailView,
                                 CreateView,
                                 UpdateView,
                                 DeleteView
)

from django.db import connection
import psycopg2
import folium as fm
import branca 
from folium.plugins import MarkerCluster
from django.core import serializers
from django.core.serializers import serialize

import json
from django.http import HttpResponse
import ast
import geopandas as gpd
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap
from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.measure import D
from django.contrib.gis import geos


from jinja2 import Template
from django.db.models import Q
from time import sleep
from django.template.defaultfilters import slugify
from taggit.models import Tag


#function to get sql and return json
def sqlToJson(fetchedSql):
    y = json.dumps(fetchedSql)
    x = json.loads(y)
    jsonfile = []
    for hh in x:
        jsonfile.append(", ".join( repr(e) for e in hh )) 
        
    results_parsed = [ast.literal_eval(x) for x in jsonfile] #removing ""
    return results_parsed

def home(request):
    #posts = Post.objects.all()
    # join blog_post and auth_user tables containing user and post info
    # finally it orders post by date_posted descending in order to show new posts on top
   
    '''
    sql = ("SELECT row_to_json(r) FROM (SELECT * FROM blog_post JOIN auth_user ON blog_post.author_id = auth_user.id) as r ORDER BY r.date_posted DESC; ")
    getPosts = connection.cursor()
    getPosts.execute(sql)
    postsql = getPosts.fetchall()
    posts_json = sqlToJson(postsql)
    #print(posts_json)
    '''
    context = {
        'posts' :  Post.objects.all(), #posts_json
        'title': 'home',
    }
    return render(request, 'blog/home.html', context)

#classbased view
class PostListView(ListView):
    model = Post
    #it needs a template with this structure: appname/modelname_viewtype(list).html
    template_name = 'blog/home.html' # we could also put the name in urls.py in as_view()
    context_object_name = 'posts'
    # ordering posts based on dates (-) put newest to top and without (-) the old posts
    # are shown at top
    ordering = ['-date_posted']
    paginate_by = 3 #for pagination which shows 3 posts in each page
    #print(Post.tags.all())

# filter posts based on tags
class TaggedList(ListView):
    model = Post
    template_name = 'blog/home.html' 
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 3 
    #print(Post.tags.all())
    def get_queryset(self):
        tagName = get_object_or_404(Tag, name = self.kwargs.get('tag'))
        print(tagName)
        return Post.objects.filter(tags__name__in=[tagName])

# recommend posts based on likes, comments and distance
class RecommendList(ListView):
   
    #print(Post.tags.all())
    likes = Like.objects.filter(post_id=35).all()
    comments = Comment.objects.filter(post_id=35).all()
    #print(comments.count(), comments.count())
    ids = Post.objects.values_list('id', flat=True)
    idList = list(ids)
    for i in idList:
        likes = Like.objects.filter(post_id=i).all()
        comments = Comment.objects.filter(post_id=i).all()
        #print("id: " , i, "likes: ",likes.count(), "comments: ",comments.count())
class PostListLocationsView(ListView):
    model = Post
    
    template_name = 'blog/post_locations.html' # we could also put the name in urls.py in as_view()
    context_object_name = 'locations'
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super(PostListLocationsView, self).get_context_data(**kwargs)
        m = fm.Map(width = 800, height = 600, zoom_start=4, location=[49.090458, 20.268874],  tiles='OpenStreetMap')
        query = Post.objects.values_list('author_id', 'title', 'geom', 'id')
        qs = list(query)
        # we add marker cluster to map and then add markers to markerCluster obj
        #marker_cluster = MarkerCluster().add_to(m)
        location_data = []
        
        user_location = Point(2.412004,48.845473, srid = 4326)
        

        #getting user_address and distance from layout template for location-based post search
        user_distance = 200000
        user_address = ""
        user_loc = Point(2.3522,48.8566, srid = 4326) #paris
        if self.request.method == 'POST':
            user_address = self.request.POST.get('user_address', None)
            user_distance = self.request.POST.get('user_distance', 2000)
            user_loc = Point(Nominatim(user_agent="ddressGeocoder").geocode(user_address).longitude, Nominatim(user_agent="ddressGeocoder").geocode(user_address).latitude, srid = 4326)
            sleep(1) # its geocoding policy
            # update the center of map based on the location of user
            m.location = [user_loc.y, user_loc.x]
            # create circle buffer with the center of user_loc and radius of 10km
            fm.Circle(location = [user_loc.y, user_loc.x],
            radius = float(user_distance)*1000, color="blue", fill_color = "#121330").add_to(m)

        #a counter to count number of posts retrieved in search
        number_of_posts = 0
        for i in qs:
            if i[2] is not None: # i[2] contains geom data and i[1] title of post, and i[3] is id of post
                
                pp= fm.Html('<a  href="'+'http://localhost:8000/post/'+str(i[3])+'/'+'"target="_blank">'+ str(i[1]) + '</a>', script=True)
                popup = fm.Popup(pp, width=100, height=50, parse_html=True)
                # filter posts based on distance from user location
                if (i[2].transform(26986, clone=True)).distance(user_loc.transform(26986, clone=True))/1000 < float(user_distance):
                    number_of_posts += 1
                    fm.Marker(
                        location = ([i[2].y, i[2].x]),
                        #it uses fontawsome icon list
                        icon = fm.Icon(color='#1c2091',icon='angellist',prefix='fa'),
                        popup =popup
                    ).add_to(m)

                    location_data.append([i[2].y, i[2].x]
                )
        
        context['number_of_posts'] = number_of_posts

        #creating heatmap
        m.add_child(HeatMap(location_data, radius=15))
        foliumMap = m._repr_html_()
        
        context['foliumMap'] = foliumMap


        return context



class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html' 
    context_object_name = 'posts'
    paginate_by = 3 

    def get_queryset(self):
        user = get_object_or_404(User, username = self.kwargs.get('username')) #kwargs is query parameter
        return Post.objects.filter(author= user).order_by('-date_posted')
    def get_context_data(self, **kwargs):
        user_name = get_object_or_404(User, username = self.kwargs.get('username'))
        selectedUserId = Post.objects.filter(author= user_name).values_list('author_id', flat=True)
        pro = Profile.objects.get(user_id = selectedUserId[0])
        email = User.objects.filter(username= user_name).values_list('email', flat=True)
        first_name = User.objects.filter(username= user_name).values_list('first_name', flat=True)
        first_name =  first_name[0]
        #print(first_name)
        last_name = User.objects.filter(username= user_name).values_list('last_name', flat=True)
        last_name = last_name[0]
        email = email[0]
        context = super(UserPostListView, self).get_context_data(**kwargs)
        
        context['imageUrl'] = pro.image.url
        context['username'] = user_name
        context['email'] = email
        context['about'] = pro.about
        context['first_name'] = first_name
        context['last_name'] = last_name
        return context
        


#class based view for each post details
class PostDetailView(DetailView, ModelFormMixin):
    model = Post
    form_class = CommentForm
    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)
        # Explicitly states what get to call:
        return DetailView.get(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        # When the form is submitted, it will enter here
        self.object = None
        self.form = self.get_form(self.form_class)

        #getting like info
        liked_post_id = request.POST.get('blogpost_id', None)
        liker_id = request.user.id
        liker_username = request.user.username
        #print(liked_post_id)
        likes_connected = Like.objects.filter(post_id = liked_post_id)
        # check if the current user did not like the post before
        if liked_post_id: #if user liked the post
            if Like.objects.filter(Q(post_id = liked_post_id) & Q(user_id = request.user.id)).exists():
                pass
            else:
                p = Like(post_id=liked_post_id, user_id = liker_id, liker_username = liker_username)
                p.save()
                #print(likes_connected)
        

        if self.form.is_valid():
            postId  = self.kwargs['pk']
            self.object = self.form.save(commit=False) # commit = false prevents save form in DB
            self.object.post_id = postId
            loggediuserId = request.user.id # get current loggedin user Id
            self.object.user_id = loggediuserId
            loggediuser_username = request.user.username
            self.object.commenter_username = loggediuser_username
            prof = Profile.objects.get(user_id = loggediuserId)
            self.object.commenter_profile_id = prof.id
            self.object.commenter_profile_image = prof.image.url
            #(prof.image.url)
            self.object.save()
            # Here ou may consider creating a new instance of form_class(),
            # so that the form will come clean.
        
        # Whether the form validates or not, the view will be rendered by get()
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        
        #getting postId
        postId  = self.kwargs['pk']
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['comment_form'] = self.form
        comments = Comment.objects.filter(post_id=postId).all()
        context['comments'] = comments
        context['comments_count'] = comments.count()

        likes = Like.objects.filter(post_id=postId).all()
        context['likes_count'] = likes.count()
        foliumMap = fm.Map(width = 800, height = 600, zoom_start=6, location=[46.861588, 2.293399],  tiles='openstreetmap')

        # check if post have location data
        if Post.objects.get(id=postId).geom is not None:
            #getting lat lng from the geom column of the post using post id
            lat = Post.objects.get(id=postId).geom.y
            lng = Post.objects.get(id=postId).geom.x

            #to set marker the popup as post title
            popup = Post.objects.get(id=postId).title
            foliumMap = fm.Map(width = 800, height = 600, zoom_start=12, location=[lat, lng],  tiles='openstreetmap')
            fm.Marker(
                [lat, lng], popup=popup).add_to(foliumMap)
            foliumMap = foliumMap._repr_html_()
        
            context['foliumMap'] = foliumMap
        return context
        
    
# to create new post
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'tags', 'address']

    def form_valid(self, form):
        #tells that the post is for current logged in user
        form.instance.author = self.request.user
        newpost = form.save(commit=False)
       
        
        return super().form_valid(form)



# to update a post
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'address']

    def form_valid(self, form):
        #tells that the post is for current logged in user
        form.instance.author = self.request.user
        return super().form_valid(form)
    #check if the user is the author of the post
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

# to delete post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/' # is success, then redirect to homepage
     #check if the user is the author of the post
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

         

def about(request):
    context = {
      
        'title': 'about',
    }
    return render(request, 'blog/about.html', context)

