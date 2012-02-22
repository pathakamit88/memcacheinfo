from django.conf.urls.defaults import *

urlpatterns = patterns('memcacheinfo.views',
    url( r'^$', 'memcache_home', name = 'memcache_home' ),
    url( r'^key/$', 'memcache_keyinfo', name = 'memcache_keyinfo' ),
    url( r'^allkeys/$', 'memcache_showkeys', name = 'memcache_showkeys' ),
    url( r'^restart/$', 'memcache_flush', name = 'memcache_flush' ),
    url( r'^delete_key/$', 'delete_key', name = 'memcache_delete_key' ),
    url( r'^server_info/$', 'server_statics', name = 'memcache_server_statics' ),
)