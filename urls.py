from django.conf.urls.defaults import patterns, include, url


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'leukosia.views.home', name='home'),
    # url(r'^leukosia/', include('leukosia.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    
    
    # url for rendering the main contents
    url(r'^login/', 'webfrontend.views.render_login',name='index'),
    url(r'^$', 'webfrontend.views.main',name='main'),
    url(r'^logout/', 'webfrontend.views.logout_view',name='logout'),
    
    url(r'^station/(?P<port>\w+)/$', 'webfrontend.views.station', name='station'),
    url(r'^overview/(?P<rendertype>\w+)/$', 'webfrontend.views.overview', name='overview'),
    url(r'^stationheader/', 'webfrontend.views.stationheader', name='stationheader'),
    
    url(r'^queue/', 'webfrontend.views.queue', name='queue'),
    url(r'^nowplaying/', 'webfrontend.views.nowplaying', name='nowplaying'),
    url(r'^search/', 'webfrontend.views.search', name='search'),
    
    url(r'^listen/', 'webfrontend.views.listen', name='toggle_audio'),
    url(r'^render-player/', 'webfrontend.views.render_player', name='render_player'),
    url(r'^register-listen-port/(?P<port>\w+)/$', 'webfrontend.views.register_listen_port', name='register_listen_port'),

    url(r'^mpd/', 'webfrontend.views.mpd', name='mpd'),
    url(r'^add/', 'webfrontend.views.add', name='add'),

    
   
    
    # urls for rendering dynamic content
    #url(r'^render-station-overview/', 'webfrontend.views.render_station_overview'),
    #url(r'^render-station-details/', 'webfrontend.views.render_station_details'),
    #url(r'^render-station-details-playqueue/', 'webfrontend.views.render_station_details_playqueue'),
    #url(r'^render-station-details-playlists/', 'webfrontend.views.render_station_details_playlists'),
    #url(r'^render-station-details-library-artist/', 'webfrontend.views.render_station_details_library_artist'),
    #url(r'^render-station-details-library-album/', 'webfrontend.views.render_station_details_library_album'),
    #url(r'^render-station-details-library-folder/', 'webfrontend.views.render_station_details_library_folder'),

    url(r'^render-chat/', 'webfrontend.views.render_chat'),
    #url(r'^save-settings/', 'webfrontend.views.save_settings'),
    
    url(r'^update-database/', 'webfrontend.views.update_songdatabase'),
    
    # urls for posting data to server
    url(r'^post-chat/', 'webfrontend.views.post_chat'),
    
    # urls for mpd commands
    
    
    #url(r'^playqueue/', 'webfrontend.views.playqueue'),    
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    
)
