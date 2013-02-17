from django.db import models

### DataModels

class User(models.Model):
	name 			= models.CharField(max_length=200)
	pw 				= models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name

class Settings(models.Model):
	mpd_server		= models.CharField(max_length=200)
	mpd_pass		= models.CharField(max_length=200)
	lastfm_url		= models.CharField(max_length=200)
	lastfm_key		= models.CharField(max_length=200)

class Stations(models.Model):
	admin_port 		= models.IntegerField()
	stream_port 	= models.IntegerField()
	stream_name 	= models.CharField(max_length=200)
	description 	= models.CharField(max_length=200)
