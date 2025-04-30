from django.db import models



class Submission(models.Model):
    data = models.JSONField()

    def __str__(self):
        return f"Submission #{self.id}"