# -*- encoding: utf-8 -*-
"""

"""
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, ARRAY
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager,Jobs
from app.base.util import hash_pass
import flask

class User(db.Model, UserMixin):
    """
       Classe contient les informtions de chaque utilisateur
       """
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String())
    poste= Column(String)
    image = Column(Text,unique=True)

    def get_reset_token(self, expires_sec=1800):

        """
             facilite la création des jetons


            :Parameters:  *expires_sec (int)** - combien de secondes avant l'expiration de jeton


            :Return: jeton crée

                 """
        s = Serializer(flask.current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):

        """
              Vérifier les jetons


            :Parameters:  *token (str)** -  jeton


            :Return: un utilisateur avec identifiant

            """
        s = Serializer(flask.current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None




class Job(Jobs.Model):
    """
       Classe contient les informtions de chaque offre d"emploi
       """
    __tablename__ = 'JobOffer'

    id = Jobs.Column(Jobs.Integer, primary_key=True)
    title = Jobs.Column(Jobs.String)
    description = Jobs.Column(Jobs.String)
    tags= Jobs.Column(Jobs.String)

    def __init__(self,title,description,tags):
        self.title=title
        self.description=description
        self.tags=tags