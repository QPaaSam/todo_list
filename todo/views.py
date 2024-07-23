from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView,CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

#this ensures that user is automatically logged in after registering
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

 # this makes sure a logged in user is sent to the tasks page ie. doesn't access a login or register page   
    def get(self,*args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class Tasklist(LoginRequiredMixin,ListView):
    model = Task
    context_object_name = 'tasks' #this overides the default queryset name of 'object_list' to tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user) #This displays task created by a particular user
        context['count'] = context['tasks'].filter(complete=False).count() #This counts the tasks which are not completed
        
        #This handles the search process
        search_input = self.request.GET.get('search-area') or '' #this states that a search input can be whatever is typed inside the search box or an empty string('') ie it'll be blank if nothing is searched
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__icontains=search_input)   #this searches through the tasks list for the task that contains the search input
        return context 


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'todo/task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

# This allows the user creating the task to be automatically set to the logged in user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate,self).form_valid(form) 


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')