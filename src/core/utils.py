import importlib

from aiohttp import web

def redirect(request, view_name, **kwargs):
    location = request.app.router[view_name].url_for(**kwargs)
    raise web.HTTPFound(location=location)

def add_message(request, kind, message):
    """ Put message into session """
    messages = request.session.get('messages', [])
    messages.append((kind, message))
    request.session['messages'] = messages
    
def get_messages(request):
    """ Get messages from session and empty """
    messages = request.session.get('messages', [])
    request.session['messages'] = []
    return messages


tags = {'get_messages': get_messages}


