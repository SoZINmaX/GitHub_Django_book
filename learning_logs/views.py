from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import EntryForm, TopicForm
from django.contrib.auth.decorators import login_required
from django.http import Http404

def check_topic_owner(request, topic):
    if topic.owner != request.user:
        raise Http404
    
def index(request):
    return render(request, "learning_logs/index.html")

@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    #check if topic can be viewed by current user
    check_topic_owner(request, topic)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic,
               'entries': entries
               }
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    if request.method != 'POST':
        #no data was sent, create empty form
        form = TopicForm()
    else:
        # sent POST, manage data
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
            
    #show empty or invalid form
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    ''' Add new entry to a particular Topic'''
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        #no data was sent, create empty form
        form = EntryForm()
    else:
        # sent POST, manage data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
            
    #show empty or invalid form
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    '''Edit an existing entry.'''
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)
    if request.method != 'POST':
        #initial request, pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    else:
        # sent POST, process data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form':form}
    return render(request, 'learning_logs/edit_entry.html', context)
    
        