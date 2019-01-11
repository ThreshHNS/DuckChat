from aiohttp import web
from  chat.models import Room
import aiohttp_jinja2


class FormView(web.View):
    """
    View for register users
    """

    template = ''
    form_class = ''

    async def post(self):
        data = await self.request.post()
        form = self.form_class(data)
        context = await self.form_valid(form)
        print("здесь")

        response = aiohttp_jinja2.render_template(self.template,
                                                  self.request,
                                                  context)
        return response
    
    @aiohttp_jinja2.template(template)
    async def get(self):
        form = self.form_class()
        context = {'form': form }
        response = aiohttp_jinja2.render_template(self.template,
                                                  self.request,
                                                  context)
        return response
    
    async def form_valid(self, form):
        pass
    
    async def form_invalid(self, form):
        return {'form': form}