from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_jwt import exceptions,initialize
from sanic_jwt.decorators import protected
from sanic_openapi import swagger_blueprint
from db import *
import hashlib, binascii
import os

async def authenticate(request, *args, **kwargs):
    username = request.json.get('username',None)
    password = request.json.get('password',None)
    hash_password = hashlib.sha256(str(password).encode('utf-8')).hexdigest()

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password")
    else:
        try:
            user = User.get(username = username, password = hash_password)
        except:
            raise exceptions.AuthenticationFailed("Invalid username or password")
    return {"user_id": user.id}


app = Sanic(__name__)
initialize(app, authenticate = authenticate)

class UserRegister(HTTPMethodView):
    async def post(self,request):
        message = {}
        username = request.json.get('username',None)
        password = request.json.get('password',None)
        if not username or not password:
            message['error'] = "username and password required"
        else:
            try:
                query_user = User.get(username = username)
                message['error'] = "This username is already exist"
            except:
                hash_password = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
                create_user = User.create(username = username, password = hash_password)
                create_user.save()
                return json({"success":"User created successfully."})
        return json({'error': message})


class TweetList(HTTPMethodView):
    async def get(self,request):
        tweets = []

        for tweet in Tweet.select():
            tweets.append({'id': tweet.id, 'user': str(tweet.user.username), 'message': tweet.message, 'is_published': tweet.is_published, 'created': tweet.created})
        return json(tweets)

    async def post(self, request):
        message = {}
        message = request.json.get('message',None)

        if message is None:
            message['error'] = "Message is required"
        else:
            create_tweet = Tweet.create(user = 1, message = message)
            create_tweet.save()
            return json({'success': 'Tweet posted successfully'})
        return json({'error':message})

class TweetDetails(HTTPMethodView):
    async def get(self,request,pk):
        try:
            tweet = Tweet.get(id = pk)
            # tweet_detail = {'id': tweet.id, 'user': str(tweet.user.username), 'message': tweet.message, 'is_published' : tweet.ispublished, 'created': tweet.created}
            return json({'id': tweet.id,'message': tweet.message})
        except:
            return json({'error': 'no record found'})

    async def put(self,request,pk):
        message = {}
        try:
            instance = Tweet.get(id = pk)
        except:
            return json({'error': 'no record found'})
        
        message = request.json.get('message',None)

        if message is None:
            message['error'] = "Message is required"
            return json({'error': message})
        else:
            instance.message = message
            instance.save()
            return json({'success' : 'tweet successfully updated'})




if __name__ == "__main__":
    app.add_route(UserRegister.as_view(), '/sign-in')
    app.add_route(TweetList.as_view(), '/tweet')
    app.add_route(TweetDetails.as_view(), '/tweet/<pk:int>')
    app.run(debug = True)
