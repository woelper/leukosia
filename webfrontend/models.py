from django.db import models

### DataModels


class Settings(models.Model):
    mpd_server = models.CharField(max_length=200)
    mpd_pass = models.CharField(max_length=200)
    lastfm_url = models.CharField(max_length=200)
    lastfm_key = models.CharField(max_length=200)


class Stations(models.Model):
    admin_port = models.IntegerField(primary_key=True)
    stream_port = models.IntegerField()
    stream_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    stream_url = models.CharField(max_length=200)

    class Meta:
        ordering = ["admin_port"]

    def __unicode__(self):
        return self.stream_name
        

class Chat(models.Model):
    c_username = models.CharField(max_length=200)
    c_content = models.CharField(max_length=200)
    c_timestamp = models.DateTimeField()
    #def save(self):
    #	self.c_timestamp = datetime.now()
    #	super(Chat, self).save()

