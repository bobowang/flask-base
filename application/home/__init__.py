from flask import Blueprint, render_template
from flask_security import login_required, current_user

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.route('/test')
@login_required
def test():
    return "%s login in" % (current_user.username)
