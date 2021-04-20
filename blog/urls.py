from django.urls import path
from .views import (PostListView,
                    PostDetailView,
                    PostCreateView,
                    PostUpdateView,
                    PostDeleteView,
                    UserPostListView,
                    PostListLocationsView,
                    TaggedList,
) #classbased view
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'), # class-based view. the name is used for html href
    path('post/(?P<tag>\w+)/$', TaggedList.as_view(), name='blog-tag'), 

    path('post/locations/', PostListLocationsView.as_view(), name='post-locations'), 
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'), #<username> is url variable
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'), 
    path('post/new/', PostCreateView.as_view(), name='post-create'), 
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'), 
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'), 
    path('about/', views.about, name='blog-about'),
]
