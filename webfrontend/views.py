import time
import datetime
import logging
import urllib, urllib2

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
try:
    import simplejson as json
except ImportError:
    import json
    
from webfrontend.models import *
from mpd import MPDClient, MPDError, CommandError

logger = logging.getLogger(__name__)


### Settings

#mpd settings
HOST = Settings.objects.all()[0].mpd_server.encode('utf_8')
PASSW = Settings.objects.all()[0].mpd_pass.encode('utf_8')


#port settings
STATIONS = []
for e in Stations.objects.all():
	
	dict = model_to_dict(e)
	
	STATIONS.append(dict)
	

#last.fm settings
API_URL = Settings.objects.all()[0].lastfm_url.encode('utf_8')
API_KEY = Settings.objects.all()[0].lastfm_key.encode('utf_8')





### Helper Functions 

#login
def authenticate(username=None, password=None):
	print username
	print password
	from django.contrib.auth import authenticate
	user = authenticate(username=username, password=password)
	if user is not None:
		# the password verified for the user
		if user.is_active:
			msg = "User is valid, active and authenticated"
		else:
			msg = "The password is valid, but the account has been disabled!"
	else:
		# the authentication system was unable to verify the username and password
		msg = "The username and password were incorrect."
	return user, msg

#mpd
def get_current_song(port):
	client = MPDClient()
	client.connect(HOST,port)
	client.password(PASSW)
	cur_song = client.currentsong()
	cur_song['time'] = str(datetime.timedelta(seconds=int(cur_song['time'])))
	client.close()
	client.disconnect() 
	return cur_song

#lastfm
def get_album_cover(artist,album):
	
	kwargs={}
	kwargs.update({
          "api_key":  API_KEY,
          "format":   "json",
          "artist":artist,
          "album":album,
          "method":"album.getInfo"
        })
	url = API_URL + "?" + urllib.urlencode(kwargs)
	data = urllib2.urlopen( url )
	response_data = json.load( data )
	data.close()
	return response_data['album']['image'][3]['#text']

def get_artist_image(artist):
	kwargs={}
	kwargs.update({
          "api_key" : API_KEY,
          "format" : "json",
          "artist" : artist,
          "method" : "artist.getInfo"
        })
	url = API_URL + "?" + urllib.urlencode(kwargs)
	data = urllib2.urlopen( url )
	response_data = json.load( data )
	data.close()
	return response_data['artist']['image'][3]['#text'], response_data['artist']['bio']['summary']

def get_lastfm_albuminfo(request):
	albumcoverurl = get_album_cover(request.POST['artist'],request.POST['album'])
	response =  {'albumcoverurl':albumcoverurl}
	return HttpResponse(json.dumps(response),mimetype="application/json")

def get_lastfm_artistinfo(request):
	artistimageurl, artistbio = get_artist_image(request.POST['artist'])
	response =  {'artistimageurl':artistimageurl,'artistbio':artistbio}
	return HttpResponse(json.dumps(response),mimetype="application/json")


### Controls

def logincontrol(request):
	error = ""
	
	if request.method == 'POST':
		username = request.POST['username'].encode('utf-8')
		password = request.POST['password'].encode('utf-8')
		cur_user, error = authenticate(username, password)
		if cur_user and cur_user.is_active:
			login(request, cur_user)
			return HttpResponseRedirect('/radiostations')
	return render_to_response('login.html',{'error':error},context_instance=RequestContext(request))
	
	
def radiostations(request):
	for e in STATIONS:

		genres = {}
		try:
			cur_song = get_current_song(str(e['admin_port']))
			genre = cur_song['genre']
		except:
			try:
				cur_song = get_current_song(str(e['admin_port']))
				genre = cur_song['genre']
			except:
				genre = "nix"
		e['genre'] = genre
	return render_to_response('stations.html',{'stations':STATIONS},context_instance=RequestContext(request))


def nowplaying(request):
	station_port = request.GET['station_port']
	
	current_song = get_current_song(station_port.encode('utf-8'))
	if request.method == 'POST':
		return HttpResponse(json.dumps(current_song),mimetype="application/json")
	for e in STATIONS:
		if e['admin_port'] == int(station_port):
			station_name = e['stream_name']

	return render_to_response('nowplaying.html',{'cur_song':current_song,'station_port':station_port,'station_name':station_name},context_instance=RequestContext(request))


def playqueue(request):
	return render_to_response('playqueue.html',{},context_instance=RequestContext(request))
	

def mpdcommands(request):
	port = request.GET['port'].encode('utf-8')
	mpdcommand = request.GET['mpdcommand'].encode('utf-8')
	client = MPDClient()
	client.connect(HOST,port)
	client.password(PASSW)
	if mpdcommand == "get_current_song":
		client.get_current_song()
	elif mpdcommand == "play":
		client.play()
	elif mpdcommand == "next":
		client.next()
	elif mpdcommand == "previous":
		client.previous()
	elif mpdcommand == "pause":
		client.pause()
	elif mpdcommand == "stop":
		client.stop()
	client.disconnect()
	return HttpResponse()
	
def get_chat(request):
	response = []
	chats = Chat.objects.order_by('-c_timestamp').all()[:10]
	for chat in chats:
		response.append({'content':chat.c_content,'author':chat.c_username})
	print response
	return HttpResponse(json.dumps(response),mimetype="application/json")

def chatpush(request):
	from datetime import datetime
	content	 = request.POST['chat_content'].encode('utf-8')
	if request.user.first_name != "":
		author = request.user.first_name
	else:
		 author = str(request.user)
	t = datetime.now()
	chat_obj = Chat(c_content=content,c_username = author,c_timestamp = t)
	chat_obj.save()
	return HttpResponse()
