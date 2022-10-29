
from django.db import models
from django.contrib.auth.models import User


class Dialog(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dialog1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE)
    last_message_time = models.DateTimeField(auto_now=True)


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='message')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return self.text
