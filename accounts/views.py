from aiohttp import web

import aiohttp_jinja2

from core.routes import routes
from core.utils import redirect
from core.utils import add_message
from core.form import FormView

from .forms import SignUpForm, LogInForm
from .models import User 
from .utils import encrypt_password, verify_password, login_user, logout
from .decorators import login_required, anonymous_required


@routes.view('/register/', name='register')
class SignUp(FormView):
    """
    View for register users
    """
    
    template = 'accounts/register.html'
    form_class = SignUpForm

    @anonymous_required
    async def form_valid(self, form):
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password_repeat = form.password_repeat.data

        user_match = await User.query.where(User.username == username).gino.first()
        email_match = await User.query.where(User.email == email).gino.first()

        if user_match or email_match:
            add_message(self.request, 'danger', f'Username or email already taken')
            redirect(self.request, 'register')

        if password != password_repeat:
            add_message(self.request, 'warning', f'Password confirmation does not match')
            redirect(self.request, 'register')
            
        password = encrypt_password(password)
        await User.create(
            username=username,
            email=email,
            password=password
        )
        redirect(self.request, 'login')
    

@routes.view('/', name='login')
class SignIn(FormView):
    """ 
    View for login users 
    """

    template = 'accounts/login.html'
    form_class = LogInForm
    
    @anonymous_required
    async def form_valid(self, form):
        password = form.password.data
        email = form.email.data

        user = await User.query.where(User.email == email).gino.first()
        if not user or not verify_password(password, user.password):
            return {'form': form, 'error_msg': 'Email or password is incorect'}
        login_user(self.request, user)
        redirect(self.request, 'create_room')
        


@routes.view('/logout/', name='logout')
class LogOut(web.View):
    """
    Views for logout user
    """
    @login_required
    async def get(self):
        logout(self.request)
        redirect(self.request, 'login')