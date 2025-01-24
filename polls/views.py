from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import Http404


from .models import Question, Choice, UserVote
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

# Get questions and display them
# @login_required
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

# Show specific question and choices
@login_required
def detail(request, question_id):
  try:
    question = Question.objects.get(pk=question_id)
  except Question.DoesNotExist:
    raise Http404("Question does not exist")
  return render(request, 'polls/detail.html', { 'question': question })

# Get question and display results
# @login_required
# def results(request, question_id):
#   question = get_object_or_404(Question, pk=question_id)
#   return render(request, 'polls/results.html', { 'question': question })

@login_required
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Fetch the user's vote record for this question
    user_vote = UserVote.objects.filter(user=request.user, question=question).first()

    # Pass the user's vote count to the template
    context = {
        'question': question,
        'user_vote_count': user_vote.vote_count if user_vote else 0,  # Default to 0 if no vote exists
    }
    return render(request, 'polls/results.html', context)

# Vote for a question choice
# @login_required
# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Check if the user has already voted on this question
    user_vote = UserVote.objects.filter(user=request.user, question=question).first()
    if user_vote and user_vote.vote_count >= 1:
        # Show an error message if the user has already voted
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Sorry, you can only vote once for this question.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Show an error message if no choice is selected
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # Increment the vote count for the selected choice
        selected_choice.votes += 1
        selected_choice.save()

        # Increment the user's vote count in the UserVote table
        if not user_vote:
            user_vote = UserVote.objects.create(user=request.user, question=question, vote_count=1)
        else:
            user_vote.vote_count += 1
            user_vote.save()

        # Redirect to the results page
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))



@login_required
def resultsData(request, obj):
    votedata = []

    question = Question.objects.get(id=obj)
    votes = question.choice_set.all()

    for i in votes:
        votedata.append({i.choice_text:i.votes})

    return JsonResponse(votedata, safe=False)
