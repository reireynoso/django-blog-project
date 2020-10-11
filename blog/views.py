from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from blog.models import Post, Comment 
from blog.forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.utils import timezone

# Create your views here.

class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post
    # template_name = ".html"
    
    # attempting a sql query on the model
    def get_queryset(self):
        # Grab the Post model, all the objects, and filter based on the conditions

        # published_date is the field. Adding __ attempts a field query. In this case lte, less than or equal to
        # the - inside of the .order_by indicated how we want it ordered. In this case, descending. Or more recent blog post comes up at the top
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    
class PostDetailView(DetailView):
    model = Post

# providing the logingrequired mixin requires the view to be viewed only when the user is logged in
class CreatePostView(LoginRequiredMixin,CreateView):
    # attribute to setup in the event that someone is not logged in
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post 

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post 

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post

    # provide once deleted succesfully 
    # with the reverse_lazy, it waits until you've actually deleted to give back the success_url that you'll be going to
    success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'

    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')
    
#####################################
#####################################
@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish
    return redirect('post_detail',pk=pk)

@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post 
            comment.save() 
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request,'blog/comment_form.html', {'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    # method is defined in the models
    comment.approve() 
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk 
    comment.delete()
    return redirect('post_detail', pk=post_pk)