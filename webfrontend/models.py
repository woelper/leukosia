from django.db import models
from django.contrib.auth.models import User
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
	
	def __unicode__(self):
		return self.c_content

class Artist(models.Model):
	name = models.CharField(max_length=200, blank=True)
	lastfm_genre = models.CharField(max_length=100, null=True, blank=True)
	lastfm_bio = models.CharField(max_length=20000, null=True, blank=True)
	lastfm_coverimage = models.CharField(max_length=150, null=True, blank=True)
	lastfm_images = models.CharField(max_length=1000, null=True, blank=True)
	lastfm_name = models.CharField(max_length=100, null=True, blank=True)
	lastfm_similar_artists = models.CharField(max_length=1500, null=True, blank=True)
	album_count = models.IntegerField(null=True, blank=True)
	track_count = models.IntegerField(null=True, blank=True)
	last_modified = models.DateTimeField()
	
	def save(self):
		from datetime import datetime
		self.last_modified = datetime.now()
		super(Artist, self).save()
	
	def __unicode__(self):
		return self.name

class Album(models.Model):
	artist = models.ForeignKey(Artist)
	name = models.CharField(max_length=200)
	
	lastfm_cover = models.CharField(max_length=150, null=True, blank=True)
	lastfm_wiki_content = models.CharField(max_length=5000, null=True, blank=True)
	lastfm_release_year = models.CharField(max_length=4, null=True, blank=True)
	track_count = models.IntegerField(null=True, blank=True)
	last_modified = models.DateTimeField()
	
	def save(self):
		from datetime import datetime
		self.last_modified = datetime.now()
		super(Album, self).save()
	
	def __unicode__(self):
		return self.name

class Song(models.Model):
	mpd_path = models.CharField(max_length=300)
	artist = models.ForeignKey(Artist, null=True, blank=True)
	album = models.ForeignKey(Album, null=True, blank=True)
	title = models.CharField(max_length=200, blank=True)
	time = models.CharField(max_length=10, blank=True)
	album_pos = models.CharField(max_length=10, blank=True)
	last_modified = models.DateTimeField()
	last_modified_mpd = models.DateTimeField(null=True, blank=True)
	
	def save(self):
		from datetime import datetime
		self.last_modified = datetime.now()
		super(Song, self).save()
	
	def __unicode__(self):
		return self.mpd_path

class SongPlayed(models.Model):
	song = models.ForeignKey(Song)
	user = models.ForeignKey(User)
	date = models.DateTimeField()
	
	def __unicode__(self):
		return self.song.title + ", " + str(self.user)	
	def save(self):
		from datetime import datetime
		self.date = datetime.now()
		super(SongPlayed, self).save()
