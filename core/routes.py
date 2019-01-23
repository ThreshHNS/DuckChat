from aiohttp import web

routes = web.RouteTableDef()

import accounts.views
import chat.views