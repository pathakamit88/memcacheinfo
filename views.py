import datetime
from django import http
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.cache import cache

"""
Aimed at extracting information about a memcached server and the keys available.
test_memcache extends functionalities provided in memcache.py
To know more about memcached visit http://memcached.org/
"""

def memcache_flush( request ):
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404

    if request.method == 'POST':
        try:
            cache.clear()
        except Exception:
            pass

    return HttpResponseRedirect( reverse( 'memcache_home' ) )

def memcache_showkeys(request):
    """
    Displays all the keys and the size for the memcache server IP entered, takes by default 127.0.0.1:11211.
    Requires user login with a staff status set true.
    """
    
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404

    if request.method == "POST":
        try:
            import memcache
        except ImportError:
            raise http.Http404

        connection_string = '127.0.0.1:11211'

        host = memcache._Host(connection_string)
        host.connect()

        #getting all keys and size
        keyno_dict = {}
        host.send_cmd("stats items")
        while 1:
            line = host.readline().split(None, 2)
            if line[0] == "END":
                break

            if 'number' in line[1]:
                keyno = line[1].split(':')[1]
                item_size = line[2]
                keyno_dict[keyno] = item_size

        key_size_dict = {}
        for x,y in keyno_dict.items():
            cmd = 'stats cachedump ' + x +' '+ y
            host.send_cmd(cmd)
            while 1:
                temp = host.readline().split(None, 2)
                if temp[0] == "END":
                    break
                keyname = temp[1]
                keysize = temp[2].split()[0].replace('[','')
                try:
                    key_size_dict[keyname] = int(keysize)
                except:
                    key_size_dict[keyname] = 0

        host.close_socket()
        import operator
        soted_key_value_dict =sorted(key_size_dict.iteritems(), key=operator.itemgetter(1))

        return render_to_response('show_keys.html', locals(), context_instance = RequestContext(request) )
    else:
        return HttpResponseRedirect(reverse(memcache_home))

def memcache_home(request):
    """
    Enables user to enter IP address and port number for memcache server and returns the
    cache status(information about the complete cache). 
    Requires user login with a staff status set true.
    """
    
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404
    return render_to_response("memcache_home.html", context_instance = RequestContext(request) )

def memcache_keyinfo(request):
    """
    Displays key status(cache info like cache_hits, memory usage..)
    Requires user login with a staff status set true.
    """
    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404
    
    if request.method == 'POST':
        if request.POST.get('key_name', None):
            key = request.POST['key_name']
            if cache.get(key, None):
                data = cache.get(key)
                key_in_cache = True
            else:
                key_in_cache = False
                data = 'This key is not in cache.'
            return render_to_response("key_info.html", locals(), context_instance = RequestContext(request))
        else:
            return HttpResponseRedirect(reverse(memcache_home))
    else:
        return HttpResponseRedirect(reverse(memcache_home))

def delete_key(request):

    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404

    if request.method == 'POST':
        if request.POST.get('key_name', None):
            key = request.POST['key_name']
            if cache.get(key, None):
                cache.delete(key)
        return HttpResponseRedirect(reverse(memcache_home))
    else:
        return HttpResponseRedirect(reverse(memcache_home))

def server_statics(request):

    if not (request.user.is_authenticated() and request.user.is_staff):
        raise http.Http404

    if request.method == 'POST':
        try:
            import memcache
        except ImportError:
            raise http.Http404

        connection_string = '127.0.0.1:11211'

        host = memcache._Host(connection_string)
        host.connect()
        host.send_cmd("stats")

        class Stats:
            pass
        stats = Stats()

        while 1:
            line = host.readline().split(None, 2)
            if line[0] == "END":
                break
            stat, key, value = line
            try:
                # convert to native type, if possible
                value = int(value)
                if key == "uptime":
                    value = datetime.timedelta(seconds=value)
                elif key == "time":
                    value = datetime.datetime.fromtimestamp(value)
            except ValueError:
                pass
            setattr(stats, key, value)

        try:
            stats=stats
            hit_rate=100 * stats.get_hits / stats.cmd_get
            time=datetime.datetime.now()
            host.close_socket()
        except :
            host.close_socket()
            return HttpResponseRedirect(reverse('memcache_home'))

        return render_to_response('server_status.html', locals(), context_instance = RequestContext(request) )
    else:
        return HttpResponseRedirect(reverse(memcache_home))
