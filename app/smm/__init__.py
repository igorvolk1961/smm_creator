from flask import Blueprint

bp = Blueprint('smm', __name__)

from app.smm import routes
