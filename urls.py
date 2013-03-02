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
    url(r'^$', 'webfrontend.views.render_login',name='index'),
    url(r'^main/', 'webfrontend.views.main',name='main'),
    url(r'^logout/', 'webfrontend.views.logout_view',name='main'),
   
    
    # urls for rendering dynamic content
    url(r'^render-station-overview/', 'webfrontend.views.render_station_overview'),
    url(r'^render-station-details/', 'webfrontend.views.render_station_details'),
    url(r'^render-player/', 'webfrontend.views.render_player'),
    url(r'^render-chat/', 'webfrontend.views.render_chat'),
    
    # urls for posting data to server
    url(r'^post-chat/', 'webfrontend.views.post_chat'),
    
    #url(r'^stationoverview/', 'webfrontend.views.stationoverview',name='index'),
    url(r'^playqueue/', 'webfrontend.views.playqueue'),    
    url(r'^mpd-get-song/', 'webfrontend.views.mpd_get_song'),
    
    
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    
)
