from django.db import models
import mongoengine
from mongoengine import Document, StringField, IntField, EmbeddedDocumentField

mongoengine.connect(host="mongodb://localhost:27017/users")
# Create your models here.

# Sample document from mongodb 
# {
#     "_id": {
#         "$oid": "619073d375c61ef5ae2850e2"
#     },
#     "window": {
#         "start": {
#             "$date": "2021-11-06T08:48:00.000Z"
#         },
#         "end": {
#             "$date": "2021-11-06T08:50:00.000Z"
#         }
#     },
#     "author": "Pyre",
#     "count": {
#         "$numberLong": "258"
#     },
#     "start": {
#         "$date": "2021-11-06T08:48:00.000Z"
#     },
#     "end": {
#         "$date": "2021-11-06T08:50:00.000Z"
#     },
#     "current_timestamp": {
#         "$date": "2021-11-06T17:43:00.026Z"
#     }
# }
class HWZ_Post(Document):
    author = StringField()
    count = IntField()
    current_timestamp = StringField()
    start = StringField()
    end = StringField()
    window = StringField()
    meta = {'collection': 'users'}

class User(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length = 200)

    my_post = models.ManyToManyField(
        User,
        through='Post',
        through_fields=('topic', 'user'))

    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete = models.CASCADE)

    content = models.TextField()

class PostCount(models.Model):
    user_name = models.CharField(max_length=200)
    post_count = models.IntegerField()

    def __str__(self):
        return self.user_name + " : " + str(self.post_count)
