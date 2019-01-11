from aiohttp import web
import asyncio

from gino import Gino
from aiohttp_session import session_middleware
import aioredis
from aiohttp_session.redis_storage import RedisStorage
import aiohttp_jinja2
import jinja2
import aiohttp_autoreload

import settings
from settings import logger
from core.db import db
from core.routes import routes
from accounts.middlewares import request_user_middleware
from core.utils import tags


async def init_app(loop):
    """
    Initialize app
    """

    redis_pool = await aioredis.create_pool(settings.REDIS, loop=loop)
    
    # setup middlewares
    middlewares = [
        session_middleware(RedisStorage(redis_pool)),
        request_user_middleware
    ]

    app = web.Application(middlewares=middlewares)
    app.redis_pool = redis_pool
    
    await db.set_bind(settings.DATABASE_URL)
    # Create tables
    await db.gino.create_all()

    app.router.add_static(settings.STATIC_URL, settings.STATIC_DIR, name='static')
    app.db = db

    # Jinja(template system) setup
    jinja_env = aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(settings.TEMPLATE_DIR),
        context_processors=[aiohttp_jinja2.request_processor], )
    jinja_env.globals.update(tags)
    app.add_routes(routes)
    app.wslist = {}

    app.logger = logger
    return app


async def close_app():
    """
    Close all connections
    """
    app.redis_pool.close()
    await app.redis_pool.wait_closed()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app(loop))

    if settings.DEBUG:
        aiohttp_autoreload.start()

    logger.debug(f"Start web app -  {settings.APP_HOST}:{settings.APP_PORT}")
    web.run_app(app, host=settings.APP_HOST, port=settings.APP_PORT, access_log=logger)
    
    try:
        loop.run_forever() 
    except KeyboardInterrupt:    		
        logger.warning("Keyboard Interrupt ^C")
    finally:
        logger.warning("Stop server begin")
        loop.run_until_complete(close_app())
        loop.close()    
    logger.warning("Stop server end")