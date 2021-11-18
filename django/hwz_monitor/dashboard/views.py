from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import HWZ_Post, Post
from .forms import PostForm


# Create your views here.
def index(request):
    post_list = Post.objects.all()
    #build a form object
    postForm = PostForm()
    #push post list and form object into the context
    context = {'post_list': post_list, \
        'form': postForm}

    return render(request, 'show_post.html', context)

def uploadPost(request):
    if request.is_ajax and request.method == "POST":
        # get the form data
        form = PostForm(request.POST)
        # save the data and after fetch the object in instance
        if form.is_valid():
            instance = form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [ instance, ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

def get_post_count(request):
    author_dict = {}

    for post in HWZ_Post.objects:
        author_dict[post.author] = post.count

    data = []
    labels = sorted(author_dict, key=author_dict.get, reverse=True)[:10]
    for i in labels:
        data.append(author_dict[i])
    print(data, labels)
    
    # labels.append()
    # data.append()
        # labels.append(post.author)
        # data.append(post.count)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

def get_barchart(request):
    return render(request, 'barchart.html')
