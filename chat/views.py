from datetime import datetime
import re

from aiohttp import web, WSMsgType

import aiohttp_jinja2

from core.routes import routes
from core.utils import redirect
from core.utils import add_message
from accounts.models import User
from accounts.decorators import login_required

from .models import Room, Message


@routes.view('/rooms', name='create_room')
class CreateRoom(web.View):

    template = 'chat/rooms.html'

    @login_required
    @aiohttp_jinja2.template(template)
    async def get(self):
        return {'chat_rooms': await Room.query.gino.all()}

    @login_required
    async def post(self):
        room_name = await self.is_valid()
        if not room_name:
            redirect(self.request, 'create_room')
        if await Room.query.where(Room.name == room_name).gino.first():
            add_message(self.request, 'danger', f'Room with {room_name} already exists.')
            redirect(self.request, 'create_room')
        room = await Room.create(name=room_name, created_date=datetime.now())
        redirect(self.request, 'room', slug=room.name)

    async def is_valid(self):
        data = await self.request.post()
        roomname = data.get('roomname', '').lower()
        if not re.match(r'^[a-z]\w{0,31}$', roomname):
            add_message(self.request, 'warning', f'Room name should start with letter and be alphanumeric.')
            return False
        return roomname



@routes.view('/rooms/{slug}', name='room')
class RoomDetailView(web.View):

    template = 'chat/chat.html'

    @login_required
    @aiohttp_jinja2.template(template)
    async def get(self):
        search_name = self.request.match_info['slug']
        room = await Room.query.where(Room.name == search_name).gino.first()
        if not room:
            raise web.HTTPNotFound(reason=f'Room with name {search_name} not found')
        
        return {
            'room': room, 'room_messages': await Message.query.where(Message.room_id == room.id).gino.all(),
            'chat_rooms': await Room.query.gino.all()}
        



@routes.view('/ws/{slug}', name='ws')
class RoomWebSocket(web.View):
    async def get(self):

        search_name = self.request.match_info['slug']
        room = await Room.query.where(Room.name == search_name).gino.first()

        if not room:
            raise web.HTTPNotFound(reason=f'Room with name {search_name} not found')

        self.room = room
        user = self.request.user
        app = self.request.app

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        if self.room.id not in app.wslist:
            app.wslist[self.room.id] = {}
        
        app.wslist[self.room.id][user.username] = ws
        
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    text = msg.data.strip()
                    message = await Message.create(
                        user_name=user.username,
                        room_id=room.id,
                        text=text,
                        created_date = datetime.now()
                    )
                    message.user = user
                    await self.broadcast(message)
        
        await self.disconnect(user.username, ws)
        return ws
    
    async def broadcast(self, message):
        """ Send messages to all in this room """
        for peer in self.request.app.wslist[self.room.id].values():
            await peer.send_json({'text': message.text, 'username': message.user.username, 'time':message.created_date.isoformat()})

    async def disconnect(self, username, socket, silent=False):
        """ Close connection and notify broadcast """
        app = self.request.app
        app.wslist.pop(username, None)
        if not socket.closed:
            await socket.close()
        if silent:
            return
