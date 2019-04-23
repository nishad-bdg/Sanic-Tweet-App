import datetime
from peewee import *

db = SqliteDatabase('tweet_db.db')

class BaseModel(Model):
	class Meta:
		database = db


class User(BaseModel):
	username = CharField(unique = True)
	password = CharField()
	join_date = DateTimeField(default = datetime.datetime.now())


class Follower(BaseModel):
	request_from = ForeignKeyField(User, backref = 'request_from')
	request_to = ForeignKeyField(User, backref = 'request_to')
	is_accpeted = BooleanField(default = False)
	created = DateTimeField(default = datetime.datetime.now())

class Tweet(BaseModel):
	user = ForeignKeyField(User, backref = 'tweets')
	message = TextField()
	created = DateTimeField(default = datetime.datetime.now())
	is_published = BooleanField(default = True)

def create_table():
	db.create_tables([User,Follower,Tweet])






