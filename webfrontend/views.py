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
from django.contrib.auth import authenticate, login, logout
try:
    import simplejson as json
except ImportError:
    import json


    
from mpd import MPDClient, MPDError, CommandError
#import pylast
from webfrontend.models import *

logger = logging.getLogger(__name__)



### Define MPD Object ###
class PollerError(Exception):
    """Fatal error in poller."""

class MPDPoller(object):
    """
    
    Define MPD Objects
    (http://jatreuman.indefero.net/p/python-mpd/page/ExampleErrorhandling/)
    
    """
    def __init__(self, station_port):
        self._host = HOST;
        self._port = station_port;
        self._password = PASSW;
        self._client = MPDClient()
        
    def connect(self):
        try:
            print ("Connecting to " + self._host + ":" + self._port)
            self._client.connect(self._host, self._port)
            # Catch socket errors
        except IOError as (errno, strerror):
            raise PollerError("IOError: Could not connect to '%s:%s' - %s" %
                              (self._host, self._port, strerror))
        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't know how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as e:
            raise PollerError("MPDError: Could not connect to '%s:%s' - %s" %
                              (self._host, self._port, e))
        if self._password:
            try:
                self._client.password(self._password)

            # Catch errors with the password command (e.g., wrong password)
            except CommandError as e:
                raise PollerError("Could not connect to '%s:%s' - "
                                  "password commmand failed: %s" %
                                  (self._host, self._port, e))

            # Catch all other possible errors
            except (MPDError, IOError) as e:
                raise PollerError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, e))
                
    def get_current_song(self):
        try:
            song = self._client.currentsong()
        # Couldn't get the current song, so try reconnecting and retrying
        except (MPDError, IOError):
            # No error handling required here
            # Our disconnect function catches all exceptions, and therefore
            # should never raise any.
            self.disconnect()
            try:
                self.connect()
            # Reconnecting failed
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)
            try:
                song = self._client.currentsong()
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve current song: %s" % e)
        # Hurray!  We got the current song without any errors!
        return song
    
    def get_queue(self):
        try:
            queue = self._client.playlistinfo()
        # Couldn't get the current song, so try reconnecting and retrying
        except (MPDError, IOError):
            # No error handling required here
            # Our disconnect function catches all exceptions, and therefore
            # should never raise any.
            self.disconnect()
            try:
                self.connect()
            # Reconnecting failed
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)
            try:
                queue = self._client.playlistinfo()
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        # Hurray!  We got the current song without any errors!
        for song in queue:
            song['time'] = str(datetime.timedelta(seconds=int(e['time'])))
        return queue

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()

        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            pass
        try:
            self._client.disconnect()
        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient()
        


### Globals ###

# MPD globals
HOST = Settings.objects.all()[0].mpd_server.encode('utf_8')
PASSW = Settings.objects.all()[0].mpd_pass.encode('utf_8')

# Last-fm globals
LASTFM_API_URL = Settings.objects.all()[0].lastfm_url.encode('utf_8')
LASTFM_API_KEY = Settings.objects.all()[0].lastfm_key.encode('utf_8')

#lastfm = pylast.LastFMNetwork(api_key = LASTFM_API_KEY, api_secret = 
#							"", username = "", password_hash = "")



### Helper Functions ###   
    
# login
def authenticate(username=None, password=None):
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    if user is not None:    # the password verified for the user
        if user.is_active:
            msg = "User is valid, active and authenticated"
        else:
            msg = "The password is valid, but the account has been disabled!"
    else:                    # unable to verify the username and password
        msg = "The username and/or password were incorrect."
    return user, msg
    
def get_stationlist():
	station_objects = Stations.objects.all()
	stationlist = []
	for station in station_objects:
		station = model_to_dict(station)
		stationlist.append(station)
	return stationlist


### Controls

def render_login(request):
    """
        
        renders the login page
    
    """
    error = ""
    if request.method == 'POST':
        username = request.POST['username'].encode('utf-8')
        password = request.POST['password'].encode('utf-8')
        cur_user, error = authenticate(username, password)
        if cur_user and cur_user.is_active:
            login(request, cur_user)
            return HttpResponseRedirect('/main')
    return render_to_response('login.html',
                                  {'error': error,'page': "login"},
                                  context_instance=RequestContext(request))


def main(request):
	"""

	gets html for main page on redirect after login
	and renders it

	"""
	stationlist = get_stationlist()
	# check if user is logged in, else fall back to login
	if not request.user.is_authenticated():
		error = "You are not signed in."
		return render_to_response('login.html',
								{'error': error,'page': "login"},
								context_instance=RequestContext(request))
	username = request.user.username
	return render_to_response('master.html',
							{'lastfm_key': LASTFM_API_KEY, 'lastfm_url': LASTFM_API_URL,
							'username': username, 'stationlist':stationlist, 'mpdhost': HOST},
							context_instance=RequestContext(request))


def render_station_overview(request):
	"""

	gets html for list of stations
	and renders it

	"""
	current_song = ""
	stationlist = get_stationlist()
	admin_port = request.GET['port'].encode('utf-8')
	for station in stationlist:
		if admin_port == str(station['admin_port']):
			admin_port = str(station['admin_port'])
			stream_port = str(station['stream_port'])
			stream_name = station['stream_name']
			print ('test')
	try:
		poller = MPDPoller(admin_port)
		poller.connect()
		current_song = poller.get_current_song()
		poller.disconnect()
	except:
		current_song = False
	return render_to_response('stations_stationoverview.html',
									{'current_song': current_song, 
									'admin_port':admin_port, 
									'stream_port':stream_port,'stream_name':stream_name},
									context_instance=RequestContext(request))
   
   
    
def render_station_details(request):
	"""

	gets html for details of stations
	and renders it

	"""
	station_port = request.GET['station-port'].encode('utf-8')
	print("getting songinfo for port: " + station_port)
	poller = MPDPoller(station_port)
	poller.connect()
	current_song = poller.get_current_song()
	poller.disconnect()  
	current_song['time'] = str(datetime.timedelta(seconds=int(current_song['time'])))[2:]
	#artist = lastfm.get_artist("System of a Down")
	#print artist
	#print artist.get_cover_image(4)
	
	return render_to_response('stations_stationdetails.html',
							{'current_song': current_song,
							'station_port':station_port},
							context_instance=RequestContext(request))
    

def render_player(request):
    """

    gets html for list of the 10 last chat messages
    and renders it

    """
    return render_to_response('player.html',
                              {},
                              context_instance=RequestContext(request))



def render_chat(request):
    """

    gets html for list of the 10 last chat messages
    and renders it

    """
    chatlist = []
    chatobjects = Chat.objects.order_by('-c_timestamp').all()[:10]
    for chat in chatobjects:
        chattime = str(chat.c_timestamp)[:10] + ", " + str(chat.c_timestamp)[11:16]
        chatlist.append({'content':chat.c_content,'author':chat.c_username,'timestamp':chattime})
    return render_to_response('chat_chatcontent.html',
                              {'chatlist':chatlist},
                              context_instance=RequestContext(request))
    

def post_chat(request):
    from datetime import datetime
    """

    posts a chatmessage to the database

    """
    content = request.POST['chatmessage'].encode('utf-8')
    if content and content != "":
        if request.user.first_name != "":
            author = request.user.first_name
        else:
            author = str(request.user)
        t = datetime.now()
        chat_obj = Chat(c_content=content,c_username = author,c_timestamp = t)
        chat_obj.save()
    return HttpResponse()



### Ajax ###

def playqueue(request):
    cur_playlist = get_current_playlist(request.GET['station_port'].encode('utf-8'))
    return render_to_response('playqueue.html',{'playlist':cur_playlist},context_instance=RequestContext(request))

def mpd_get_song(request):
	port = request.GET['station_port'].encode('utf-8')
	current_song = ""
	try:
		poller = MPDPoller(port)
		poller.connect()
		current_song = poller.get_current_song()
		poller.disconnect()
	except:
		current_song = False
	if current_song:
		return HttpResponse(current_song['title'])
	else:
		return HttpResponse("")


def logout_view(request):
    """
        
        logs the user out and redirects to login
    
    """
    logout(request)
    return HTTPResponseRedirect('/')('/')



