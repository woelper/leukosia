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

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^radiostations/', 'webfrontend.views.radiostations'),
    url(r'^$', 'webfrontend.views.logincontrol',name='index'),
    url(r'^main/', 'webfrontend.views.main',name='index'),
    url(r'^stationdetails/', 'webfrontend.views.stationdetails',name='index'),
    url(r'^stationoverview/', 'webfrontend.views.stationoverview',name='index'),
	url(r'^navbar/', 'webfrontend.views.navbar',name='index'),
    
    url(r'^playqueue/', 'webfrontend.views.playqueue'),
    url(r'^nowplaying/', 'webfrontend.views.nowplaying'),
    #url(r'^lastfmalbuminfo/', 'webfrontend.views.get_lastfm_albuminfo'),
    #url(r'^lastfmartistinfo/', 'webfrontend.views.get_lastfm_artistinfo'),
    url(r'^$', 'webfrontend.views.logincontrol',name='index'),
    url(r'^mpdcommands/', 'webfrontend.views.mpdcommands'),
    url(r'^ajaxchat/', 'webfrontend.views.get_chat'),
    url(r'^chatpush/', 'webfrontend.views.chatpush'),
)
