from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.http import Http404


from .models import Question, Choice, UserVote
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})



@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user_vote = UserVote.objects.filter(user=request.user, question=question).first()
    context = {
        'question': question,
        'user_vote_count': user_vote.vote_count if user_vote else 0, 
    }
    return render(request, 'polls/results.html', context)



@login_required
def vote(request, question_id):
    
    question = get_object_or_404(Question, pk=question_id)

    
    user_vote = UserVote.objects.filter(user=request.user, question=question).first()
    if user_vote:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Sorry, you can only vote once for this question.",
        })

   
    choice_id = request.POST.get('choice') 
    selected_choice = question.choice_set.filter(pk=choice_id).first()  

    
    if not selected_choice:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    
    selected_choice.votes += 1
    selected_choice.save()

    
    UserVote.objects.create(user=request.user, question=question, vote_count=1)

    return redirect('polls:results', question.id)



@login_required
def resultsData(request, obj):
    votedata = []

    question = Question.objects.get(id=obj)
    votes = question.choice_set.all()

    for i in votes:
        votedata.append({i.choice_text:i.votes})

    return JsonResponse(votedata, safe=False)
