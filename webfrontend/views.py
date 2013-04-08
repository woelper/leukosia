import time
import datetime
import logging
import urllib, urllib2
import parser
import re

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
import pylast
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
            #print ("Connecting to " + self._host + ":" + self._port)
            self._client.connect(self._host, self._port)
            # Catch socket errors
        except IOError as (errno, strerror):
            raise PollerError("IOError: Could not connect to '%s:%s' - %s" %
                              (self._host, self._port, strerror))
        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't k how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as e:
            raise PollerError("MPDError: Could not connect to '%s:%s' - %s" %
                              (self._host, self._port, e))
        except:
            pass
			
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
            except:
                pass
                
                
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
        # Hurray!  We got the current queue without any errors!
        for song in queue:
            song['time'] = str(datetime.timedelta(seconds=int(song['time'])))
        return queue
        
    def get_playlists(self):
        try:
            playlists = self._client.lsinfo()
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
                playlists = self._client.lsinfo()
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        # Hurray!  We got the current queue without any errors!
        result = []
        for playlist in playlists:
			if playlist.has_key('playlist'):
				playlist['last_modified'] = playlist['last-modified']
				result.append(playlist)
        return result
        
    def get_library(self):
        try:
            library = self._client.list('artist')
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
                library = self._client.list('artist')
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        # Hurray!  We got the current lib without any errors!
        return library
        
    def find(self, artist):
        try:
            songs = self._client.find('artist', artist)
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
                songs = self._client.find(artist)
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        # Hurray!  We got the current lib without any errors!
        return songs
    
    def get_albumlist(self, artist):
        try:
            albumlist = self._client.list('album', 'artist', artist)
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
                albumlist = self._client.list('album', 'artist', artist)
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        # Hurray!  We got the current lib without any errors!
        return albumlist
    
    def listall(self):
        try:
            library = self._client.listall()
        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)
            try:
                library = self._client.listall()
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        return library
    
    def get_status(self):
        try:
            status = self._client.status()
        
        except (MPDError, IOError):
           
            self.disconnect()
            try:
                self.connect()
            # Reconnecting failed
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)
            try:
                status = self._client.status()
            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve playlist: %s" % e)
        return status
       
    def command(self, command, key):
        try:
            if key:
                exec('self._client.' + command + '("' + key + '")')
            else:
                exec('self._client.' + command + '()')
        except (MPDError, IOError):
           print "MPD COMMAND ERROR"
        return True
	
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

lastfm = pylast.LastFMNetwork(api_key = LASTFM_API_KEY, api_secret = 
							"", username = "", password_hash = "")



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
    print msg
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
			return HttpResponseRedirect('/')
	return render_to_response('login.html',
					{'error': error,'page': "login"},
					context_instance=RequestContext(request))

def logout_view(request):
    """
        
        logs the user out and redirects to login
    
    """
    logout(request)
    return HttpResponseRedirect('/login')


def main(request):
	"""

	gets html for main page on redirect after login
	and renders it

	"""
	# check if user is logged in, else fall back to login
	if not request.user.is_authenticated():
		error = "You are not signed in."
		print request.user
		return HttpResponseRedirect('login/')
	else:
		username = request.user.username
		return render_to_response('base.html',
						{'username': username},
						context_instance=RequestContext(request))

def overview(request, rendertype):
	"""

	gets html for the overview for all station
	and renders it

	"""
	stationlist = get_stationlist()
	#session_stationlist = request.session.get('stationlist')
	
	for station in stationlist:
		station['stream_url'] = station['stream_url'].split(',')
		poller = MPDPoller(station['admin_port'])
		poller.connect()
		status = poller.get_status()
		station['current_song'] = poller.get_current_song()
		poller.disconnect()
		if station['current_song'] == {} and status['state'] == 'stop':
			try:
				queue = poller.get_queue()
				songid = status['songid']
				for q in queue:
					if q['id'] == songid:
						station['current_song'] = q
						break
			except:
				station['current_song'] = False
		
		try:	
			if status['state'] == 'play':
				station['status_display'] = "on air"
				station['badge'] = "important"
			elif status['state'] == 'pause':
				station['status_display'] = "paused"
				station['badge'] = "warning"
			elif status['state'] == 'stop':
				station['status_display'] = "stopped"
				station['badge'] = "mute"
			station['status'] = status
		except:
			station['status_display'] = "Error"
			station['badge'] = "info"
			station['status'] = False

		# get some Song Attributes from Database
		station['album'] = {}
		try:
			db_song = Song.objects.get(mpd_path = 
							station['current_song']['file'])
			station['album']['albumcover'] = db_song.album.lastfm_cover			
		except:
			pass
			
	# save stationdict in session
	stationdict = {}
	for station in stationlist:
		admin_port = station['admin_port']
		stationdict[admin_port] = station
	request.session['stationdict'] = stationdict
	
	if rendertype == "main":
		return render_to_response('overview.html',
						{'stationlist':stationlist},
						context_instance=RequestContext(request))
	elif rendertype == "left":
		return render_to_response('overview_left.html',
						{'stationlist':stationlist},
						context_instance=RequestContext(request))

	
def station(request, port):
	"""

	gets html for the station container for station with id
	and renders it

	"""
	#get stationdict
	stationdict = request.session.get('stationdict')

	request.session['admin_port'] = int(port)
	if request.method == 'GET':
		return render_to_response('station.html',
						{'station': stationdict[int(port)]},
						context_instance=RequestContext(request))
	elif request.method == 'POST':
		return HttpResponse("");
		
def stationheader(request):
	
	admin_port = request.session.get('admin_port')
	
	context_station = request.session.get('stationdict')[admin_port]
	
	poller = MPDPoller(admin_port)
	poller.connect()
	status = poller.get_status()
	poller.disconnect()
	
	context_station['status'] = status
	
	if context_station['status'].has_key('time'):
		time = status['time']
		z = time.find(":")
		elapsed = time[:z]
		songtime = time[z+1:]
		context_station['progress'] = str((int(elapsed) * 100) / int(songtime))
		elapsed = str(datetime.timedelta(seconds=int(elapsed)))
		songtime = str(datetime.timedelta(seconds=int(songtime)))
		if songtime[0] == "0":
			elapsed = elapsed [2:]
			songtime = songtime [2:]
		context_station['time'] = elapsed + " / " + songtime


	return render_to_response('stationheader.html',
					{'station': context_station},
					context_instance = RequestContext(request))
	


def queue(request):
	"""

	gets html for the queue of certain station
	and renders it

	"""
	#get requesting station from session
	try:
		poller = MPDPoller(request.session.get('admin_port'))
		poller.connect()
		queue = poller.get_queue()
		poller.disconnect()
	except:
		queue = {}
	"""
	for song in queue:
		try:
			db_song = Song.objects.get(mpd_path = 
							song['file'])
			song['key'] = str(db_song.id)
		except:
			pass
		try:
			#song['albumcover'] =  db_song.album.lastfm_cover
			song['genre'] =  db_song.artist.lastfm_genre.split(',')[0] + ", " +db_song.artist.lastfm_genre.split(',')[1]
			song['track'] = db_song.album_pos
			
		except:
			pass
	"""
	request.session['queue'] = queue
	#current_song
	
	return render_to_response('queue.html',
					{'queue': queue},
					context_instance=RequestContext(request))

def nowplaying(request):
	"""

	gets html for nowplaying of certain station 
	and renders it

	"""
	#get requesting station from session
	admin_port = request.session.get('admin_port')
	context_station = request.session.get('stationdict')[admin_port]
	try:
		context_station['artist'] = {}
		mpd_path = context_station['current_song']['file']
		db_song = Song.objects.get(mpd_path = mpd_path)
		context_station['artist']['genre'] = db_song.artist.lastfm_genre
		context_station['artist']['images'] = db_song.artist.lastfm_images
		context_station['artist']['images'] = context_station['artist']['images'].split(',')
		context_station['artist']['coverimage'] = db_song.artist.lastfm_coverimage

	except:
		pass
	
	#context_station['artist']['images'] = context_station['artist']['images'].split(',')
	return render_to_response('nowplaying.html',
					{'station': context_station},
					context_instance = RequestContext(request))
					
def search(request):
	
	artists_exact = []
	albums = []
	artists_other = []
	notfound = False
	
	try:
		searchterm = request.POST['term']
	except KeyError:
		artistid = request.POST.get('artistid')
		artist = Artist.objects.get(pk=artistid)
		searchterm = artist.name
		
	if searchterm == "":
		artists_exact = []
	else:
		artists_exact = Artist.objects.filter(name__iexact = searchterm)
		for artist in artists_exact:
			albums = Album.objects.filter(artist = artist)\
					.order_by('-lastfm_release_year')
	if len(artists_exact) < 1:
		artists_other = Artist.objects \
					.filter(name__icontains = searchterm) \
					.exclude(name__iexact = searchterm) \
					.order_by('name')
		if len(artists_other) < 1:
			notfound = True
			
	
		
	#albums_exact = Album.objects.filter(name__iexact = searchterm)
	#albums_other = Album.objects.filter(name__icontains = searchterm)
	#songs_exact = Song.objects.filter(title__iexact = searchterm)
	#songs_other = Song.objects.filter(title__contains = searchterm)
	
	#artists_all = Artist.objects.all()
	#options = []
	#for artist in artists_all:
	#	options.append(artist.name) 
	#artists_all = {'options': options}
	#artists_all = json.dumps(artists_all)
	
			
	return render_to_response('search.html',
					{'searchterm': searchterm,
					'notfound': notfound,
					#'artists_all': artists_all
					'artists_exact': artists_exact,
					'albums': albums,
					'artists_other': artists_other,
					#'albums_other': albums_other,
					#'albums_other': albums_other,
					#'songs_other': songs_other,
					#'songs_other': songs_other
					},
					context_instance = RequestContext(request))
					
def mpd(request):
	
	response = ''
	port = str(request.session.get('admin_port'))

	poller = MPDPoller(port)
	poller.connect()
	
	queue = request.session.get('queue')
	
	action = request.POST['action']
	action = action.split('-')
	command = action[0]
	try:
		key = action[1]
	except:
		key = False
		
	if command == "removesong":
		command = 'deleteid'
		poller.command(command, key)
	
	elif command == "removealbum":
		command = 'deleteid'
		album = False
		try:
			for song in queue:
				if song['id'] == key:
					if song.has_key('album'):
						album = song['album']
						break
			for song in queue:
				if song.has_key('album'):
					if song['album'] == album:
						key = song['id']
						poller.command(command, key)
		except:
			response = "error"
	
	elif command == "removeartist":
		command = 'deleteid'
		artist = False
		try:
			for song in queue:
				if song['id'] == key:
					if song.has_key('artist'):
						artist = song['artist']
						break
			for song in queue:
				if song.has_key('artist'):
					if song['artist'] == artist:
						key = song['id']
						poller.command(command, key)
		except:
			response = "error"
	
	elif command == "clearplaylist":
		command = 'clear'
		poller.command(command, key)
	
	elif command == 'random':
		session_station = request.session.get('station')
		session_stationlist = request.session.get('stationlist')
		for station in session_stationlist:
			if station['admin_port'] == session_station['admin_port']:
				status = station['status']
				break
		print status
		if status['random'] == '0':
			key = '1'
		else:
			key = '0'
		print key
		poller.command(command, key)
	
	elif command == 'repeat':
		session_station = request.session.get('station')
		session_stationlist = request.session.get('stationlist')
		for station in session_stationlist:
			if station['admin_port'] == session_station['admin_port']:
				status = station['status']
				break
		print status
		if status['repeat'] == '0':
			key = '1'
		else:
			key = '0'
		print key
		poller.command(command, key)
	
	else:
		poller.command(command, key)
		
	poller.disconnect()

	return HttpResponse(response)
	
def add(request):
	msg = ""
	port = request.session.get('admin_port')
	element_id = request.POST['element-id']
	add_type = request.POST['type']
	if add_type == "artist":
		artist = Artist.objects.get(pk = element_id)
		songs = Song.objects.filter(artist = artist)
	elif add_type == "album":
		album = Album.objects.get(pk = element_id)
		songs = Song.objects.filter(album=album)
	counter = 0
	for song in songs:
		counter = counter +1
		poller = MPDPoller(port)
		poller.connect()
		poller.command('add', song.mpd_path)
		poller.disconnect()
	msg = '<div class="alert">' + \
			'<button type="button" class="close" ' + \
			'data-dismiss="alert">&times;</button>' + \
			str(counter) + \
			' songs added to queue'
	print msg
	return HttpResponse(msg)


def render_player(request):
	"""

	gets html for the player div
	and renders it

	"""
	admin_port = request.session.get('admin_port')
	listen_station = request.session.get('stationdict')[admin_port]
	return render_to_response('player.html',
							{'listen_station': listen_station},
							context_instance=RequestContext(request))

def listen(request):
	port = request.session.get('listenport')
	station = request.session.get('stationdict')[port]
	last_song = request.session.get('last_song', False)
	save_song = request.session.get('save_song', False)
	user = request.user
	try:
		song = Song.objects.get(mpd_path = station['current_song']['file'])
		if song == last_song:
			if save_song == True or save_song == "JUST_SAVED":
				if not save_song == "JUST_SAVED":
					s = SongPlayed(user = user, song = song)
					s.save()
					request.session['save_song'] = "JUST_SAVED"
			else:
				request.session['save_song'] = True
		else:
			request.session['last_song'] = song
			request.session['save_song'] = True
	except:
		print "cannot scrobble: Song not found in Database"
	return HttpResponse("")

def register_listen_port(request, port):
	if port:
		request.session['listenport'] = int(port)
	else:
		request.session['listenport'] = False
	return HttpResponse("")




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





def save_settings(request):
	username = request.GET['username'].encode('utf-8')
	print username
	return HttpResponse("")



def update_songdatabase(request):
	poller = MPDPoller(get_stationlist()[0]['admin_port'])
	poller.connect()
	artists_mpd = poller.get_library()
	artists_mpd.sort(key=lambda s: s.lower())
	
	counter = 0
	artist_count = len(artists_mpd)
	for artist in artists_mpd[1:]:
		counter = counter + 1
		print "### progress: " + str(counter) + " / " + str(artist_count)
		print "### processing: " + artist
		
		try:
			songs_mpd = poller.find(artist)
		except:
			songs_mpd = False
		
		try:
			artist_obj = Artist.objects.get(name = artist)
		except:
			print "saving artist"
			artist_obj = save_artist_to_db(artist)
		
		albums_mpd = poller.get_albumlist(artist)
		
		for album in albums_mpd:
			try:
				album_obj = Album.objects.get(name = album)
			except:
				print "saving album: " + album
				album_obj = save_album_to_db(album, artist_obj)
				
			if songs_mpd:
				for song in songs_mpd:
					try:
						Song.objects.get(mpd_path = song['file'])
					except:
						if song.has_key('album'):
							if song['album'] == album:
								save_song_to_db(song, artist_obj, album_obj)
							else:
								pass
						else:
							save_song_to_db(song, artist_obj, None)

	poller.disconnect()
	
	#couting albums and tracks
	print "fixing album and track count..."
	for artist in Artist.objects.all():
		artist.album_count = len(Album.objects.filter(artist=artist))
		artist.track_count = len(Song.objects.filter(artist=artist))
		artist.save()
	for album in Album.objects.all():
		album.track_count = len(Song.objects.filter(album=album))
		album.save()
	
	print "done!"
	
	return HttpResponse("successss")
	
def save_song_to_db(song, artist, album):
	s = Song(mpd_path = song['file'])
	s.artist = artist
	s.album = album
	try:
		if song.has_key('title'):
			s.title = song['title']
		else:
			s.title = song['file']
		if song.has_key('time'):
			song['time'] = str(datetime.timedelta(seconds=int(song['time'])))
			if song['time'][0] == '0':
				song['time'] = song['time'][2:]
			s.time = song['time']
		if song.has_key('track'):
			try:
				pos = re.findall(r'[0-9]*',song['track'])[0].zfill(2)
				s.album_pos = pos
			except:
				pass
		if song.has_key('last-modified'):
			date = re.findall(r'[1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 
					song['last-modified'])[0]
			time = re.findall(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',
					song['last-modified'])[0]

			s.last_modified_mpd = date + " " + time
		print "saving song: " + s.title
		s.save()
	except:
		#log
		pass
	return True


def save_artist_to_db(artist):
	a = Artist(name = artist)
	try:
		lastfm_artist = lastfm.get_artist(artist)
		a.lastfm_bio = lastfm_artist.get_bio_content()
		toptags = []
		for topItem in lastfm_artist.get_top_tags(limit=6):
			toptags.append(topItem.item.get_name())
		a.lastfm_genre = ", ".join(toptags)
		a.lastfm_coverimage = lastfm_artist.get_cover_image(size=4)
		topImages = []
		for image in lastfm_artist.get_images(order='popularity',limit=8):
			topImages.append(image.sizes.original)
		a.lastfm_images = ", ".join(topImages)
		a.lastfm_name = lastfm_artist.get_name()
		topSimilar = []
		for similar in lastfm_artist.get_similar(limit=8):
			topSimilar.append(similar.item.get_name())
		a.lastfm_similar_artists = ", ".join(topSimilar)
		a.last_modified = models.DateTimeField()
	except:
		pass
	a.save()
	return a
	
def save_album_to_db(album, artist_obj):
	a = Album(artist=artist_obj, name=album)
	try:
		lastfm_album = lastfm.get_album(artist=artist_obj.name, title=album)
		a.lastfm_cover = lastfm_album.get_cover_image(size=3)
		release_date = lastfm_album.get_release_date()
		release_year = re.findall(r'[1-2][0-9][0-9][0-9]',release_date)
		if len(release_year) > 0:
			year = release_year[0]
		else:
			year = ""
		a.lastfm_release_year = year
		a.lastfm_wiki_content = lastfm_album.get_wiki_content()
	except:
		pass
	a.save()
	return a
	
"""
def update_songdatabase_(request):
	print "Updating Database..."
	print "getting data..."
	poller = MPDPoller(get_stationlist()[0]['admin_port'])
	poller.connect()
	artistlist_mpd = poller.get_library()
	artistlist_mpd.sort(key=lambda s: s.lower())
	
	#delete obsolete Artists
	print "deleting obsolete Artists..."
	artistnamelist_db = []
	artistlist_db = Artist.objects.all()
	for artist in artistlist_db:
		artistnamelist_db.append(artist.name)
		if artist.name not in artistlist_mpd:
			print "deleting artist: " + artist.name
			artist.delete()
	#save new Artists to DB
	print "saving new Artists..."
	for artist in artistlist_mpd:
		print artist
		if artist not in artistnamelist_db:
			a = Artist(name = artist)
			try:
				lastfm_artist = lastfm.get_artist(artist)
				a.lastfm_bio = lastfm_artist.get_bio_content(language=None)
				toptags = []
				for topItem in lastfm_artist.get_top_tags(limit=6):
					toptags.append(topItem.item.get_name())
				a.lastfm_genre = ", ".join(toptags)
				a.lastfm_coverimage = lastfm_artist.get_cover_image(size=4)
				topImages = []
				for image in lastfm_artist.get_images(order='popularity',limit=8):
					topImages.append(image.sizes.original)
				a.lastfm_images = ", ".join(topImages)
				a.lastfm_name = lastfm_artist.get_name()
				topSimilar = []
				for similar in lastfm_artist.get_similar(limit=8):
					topSimilar.append(similar.item.get_name())
				a.lastfm_similar_artists = ", ".join(topSimilar)
				a.last_modified = models.DateTimeField()
			except:
				pass
			print "saving artist: " + a.name
			a.save()
	artistlist_db = Artist.objects.all()
	for artist in artistlist_db:
		print "*** processing: " + artist.name
		albumlist_mpd = poller.get_albumlist(artist.name)
		albumlist_db = Album.objects.filter(artist = artist)
		songlist_mpd = poller.find(artist.name)
		songlist_db = Song.objects.filter(artist = artist)
		
		#delete obsolete Albums from DB
		for album in albumlist_db:
			if album.name not in albumlist_mpd:
				print "deleting album: " + album.name
				album.delete()
		#save new Albums to DB to DB
		albumnamelist_db = []
		for album in albumlist_db:
			albumnamelist_db.append(album.name)
		for album in albumlist_mpd:
			if album not in albumnamelist_db and album != "":
				a = Album(artist=artist, name=album)
				try:
					lastfm_album = lastfm.get_album(artist=artist, title=album)
					a.lastfm_cover = lastfm_album.get_cover_image(size=3)
					release_date = lastfm_album.get_release_date()
					print release_date
					release_year = re.findall(r'[1-2][0-9][0-9][0-9]',release_date)
					if len(release_year) > 0:
						year = release_year[0]
					else:
						year = ""
					a.lastfm_release_year = year
					a.lastfm_wiki_content = lastfm_album.get_wiki_content()
				except:
					pass
				print "saving album: " + a.name
				a.save()
				
		#delete obsolete and modified song entries from DB
		mpd_pathlist = []
		for e in songlist_mpd:
			mpd_pathlist.append(e['file'])
		for song in songlist_db:
			#delete if song not exist anymore
			if song.mpd_path not in mpd_pathlist:
				song.delete()
			else: #delete if song modified
				for e in songlist_mpd:
					if song.mpd_path == e['file']:
						date = re.findall(r'[0-9]+', 
								e['last-modified'])
						date_int = []
						for s in date:
							date_int.append(int(s))
						if song.last_modified_mpd != datetime.datetime(date_int[0],
								date_int[1], date_int[2], date_int[3],
								date_int[4], date_int[5]):
							print "deleting song: " + song.title +  " (modified)"
							song.delete()
							songlist_db = Song.objects.filter(artist = artist)

		#save new Songs to DB
		songfilelist_db = []
		for song in songlist_db:
			songfilelist_db.append(song.mpd_path)
		for song in songlist_mpd:
			if song['file'] not in songfilelist_db:
				s = Song(mpd_path = song['file'],
						artist=artist)
				if song.has_key('album'):
					s.album = Album.objects.get(name = song['album'], artist = artist)
				if song.has_key('title'):
					s.title = song['title']
				else:
					s.title = song['file']
				if song.has_key('time'):
					song['time'] = str(datetime.timedelta(seconds=int(song['time'])))
					if song['time'][0] == '0':
						song['time'] = song['time'][2:]
					s.time = song['time']
				if song.has_key('track'):
					try:
						pos = re.findall(r'[0-9]*',song['track'])[0].zfill(2)
						s.album_pos = pos
					except:
						pass
				if song.has_key('last-modified'):
					date = re.findall(r'[1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 
							song['last-modified'])[0]
					time = re.findall(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',
							song['last-modified'])[0]

					s.last_modified_mpd = date + " " + time
				print "saving song: " + s.title
				s.save()
	
	#save new Songs without Artist Info to DB
	
	poller.disconnect()
	
	#couting albums and tracks
	print "fixing album and track count..."
	for artist in Artist.objects.all():
		artist.album_count = len(Album.objects.filter(artist=artist))
		artist.track_count = len(Song.objects.filter(artist=artist))
		artist.save()
	for album in Album.objects.all():
		album.track_count = len(Song.objects.filter(album=album))
		album.save()
	
	print "done!"

	return HttpResponse("successss")
"""

