from webfrontend.models import Stations, Chat, Settings, Artist, Album, Song, SongPlayed
from django.contrib import admin

admin.site.register(Settings)
admin.site.register(Stations)
admin.site.register(Chat)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(SongPlayed)
