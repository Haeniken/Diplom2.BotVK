import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

login = 'postgres'
kod = 'Shitko77'
engine = sq.create_engine(f'postgresql+psycopg2://{login}:{kod}$@localhost:5432/dating_pair')
connection = engine.connect()
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

Base = declarative_base()

class User_VK(Base):
    __tablename__ = 'user_vk'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    second_name = sq.Column(sq.String, nullable=False)
    city = sq.Column(sq.String, nullable=False)
    datinguser = relationship('DatingUser', uselist=False, back_populates='user_vk')

    def __init__(self, vk_id, first_name, second_name, city):
        self.vk_id = vk_id
        self.first_name = first_name
        self.second_name = second_name
        self.city = city

    def __repr__(self):
        return "<User_VK('%s','%s', '%s', '%s')>" % \
               (self.vk_id, self.first_name, self.second_name, self.city)

class DatingUser(Base):
    __tablename__ = 'datinguser'

    id = sq.Column(sq.Integer, primary_key=True)
    pair_vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    second_name = sq.Column(sq.String, nullable=False)
    birth_year = sq.Column(sq.String)
    id_User_VK = sq.Column(sq.Integer, sq.ForeignKey('user_vk.vk_id'))
    user_vk = relationship('User_VK', back_populates='datinguser')
    photo = relationship('Photo', uselist=False, back_populates='datinguser')


    def __init__(self, pair_vk_id, first_name, second_name, birth_year, id_User_VK):
        self.pair_vk_id = pair_vk_id
        self.first_name = first_name
        self.second_name = second_name
        self.birth_year = birth_year
        self.id_User_VK = id_User_VK

    def __repr__(self):
        return "<DatingUser('%s','%s', '%s', '%s', '%s')>" % \
               (self.pair_vk_id, self.first_name, self.second_name, self.birth_year, self.id_User_VK)

class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    id_DatingUser = sq.Column(sq.Integer, sq.ForeignKey('datinguser.pair_vk_id'))
    datinguser = relationship('DatingUser', back_populates='photo')
    count_likes = sq.Column(sq.Integer, nullable=False)
    link_photo = sq.Column(sq.String, nullable=False)

    def __init__(self, id_DatingUser, count_likes, link_photo):
        self.id_DatingUser = id_DatingUser
        self.count_likes = count_likes
        self.link_photo = link_photo

    def __repr__(self):
        return "<Photo('%s','%s', '%s')>" % \
               (self.id_DatingUser, self.count_likes, self.link_photo)


Base.metadata.create_all(engine)
