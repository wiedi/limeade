"""Views for limeade cloud VNC"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.conf import settings
from django.http import Http404

from urlparse import urlparse

from limeade.cloud.models import Instance


@login_required
def instance_vnc(request, slug):
    """Lets view the authenticated user a VNC console.
    
    :param request: the request object
    :param slug: the virtual machine id
    
    :returns: the vnc template
    
    :raises: DoesNotExist
    """
    try:
        i = Instance.objects.get(pk=slug, owner=request.user).pk
    except Instance.DoesNotExist:
        raise Http404
    
    token = request.session.session_key
    node_host = settings.NODE_HOST
    node_port = settings.NODE_PORT
    
    return render_to_response('limeade_cloud/instance_vnc.html', {'id': i, 
    'token': token, 'host': node_host, 'port': node_port}, context_instance=RequestContext(request))


def instance_vnc_auth(request, slug, token):
    """API call for websocket to tcp proxy to get the settings.
    
    :param request: the request object
    :param slug: the virtual machine id
    :param token: the session id from the requesting user
    
    :returns: dictionary containing proxy settings
    
    :raises: ObjectDoesNotExist
    
    .. todo:: try to test within a unit test
    """
    status_code = 200
    vnc_port = 5900
    
    try:
        s = Session.objects.get(pk=token)
        user = User.objects.get(pk=s.get_decoded().get('_auth_user_id'))
        i = Instance.objects.get(pk=slug, owner=user)
    except ObjectDoesNotExist:
        status_code = 500
    
    host = urlparse(i.node.uri).netloc
    data = {
        'source_host': settings.PROXY_HOST,
        'source_port': settings.PROXY_PORT,
        'target_host': host,
        'target_port': vnc_port
    }
    
    return HttpResponse(simplejson.dumps(data), mimetype='application/json', status=status_code)
