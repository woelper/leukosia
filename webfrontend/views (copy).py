from django.shortcuts import render_to_response
from mpd import MPDClient, MPDError, CommandError

def index(request):
	poller = MPDPoller()
	poller.connect()
	cur_song = poller.poll()
	cur_status = "gg"
	cur_status = poller.status()
	
	return render_to_response('index.html',{'cur_song':cur_song,'cur_status':cur_status})



class PollerError(Exception):
    """Fatal error in poller."""


class MPDPoller(object):
    def __init__(self, host="leukosia.eu", port="6600", password="diggur!"):
        self._host = host
        self._port = port
        self._password = password
        self._client = MPDClient()

    def connect(self):
        try:
            self._client.connect(self._host, self._port)

        # Catch socket errors
        except IOError as (errno, strerror):
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, strerror))
        except MPDError as e:
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, e))
        if self._password:
            try:
                self._client.password(self._password)
            # Catch errors with the password command (e.g., wrong password)
            except CommandError as e:
                raise PollerError("Could not connect to '%s': "
                                  "password commmand failed: %s" %
                                  (self._host, e))

            # Catch all other possible errors
            except (MPDError, IOError) as e:
                raise PollerError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, e))

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()
        except (MPDError, IOError):
            pass
        try:
            self._client.disconnect()
        except (MPDError, IOError):
            self._client = MPDClient()
	
	def status(self):
		#self._client.command_list_ok_begin()       # start a command list
		#self._client.update()                      # insert the update command into the list
		#self._client.status()                      # insert the status command into the list
		#results = self._client.command_list_end()
		return "status schlecht"
			
    def poll(self):
        try:
            cur_song = self._client.currentsong()
        except (MPDError, IOError):
            self.disconnect()
            raise PollerError("Couldn't retrieve current song: %s" % e)

        return cur_song
