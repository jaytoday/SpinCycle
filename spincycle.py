import sys
import os
from datetime import datetime

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import web
import simplejson
import logging
import opentok

web.config.debug = True

openTokSDK = opentok.OpenTokSDK('364442', 'b9a4b7acb902709f867dd35529361c394c315d0f')
db = web.database(dbn='mysql', user='telephone', pw='ca4nuhearmenow', db='tokbox_spincycle')
render = web.template.render('templates/')

urls = (
	'/', 'index',
	'/api/get-session', 'get_session',
	'/api/update-session', 'update_session',
	'/api/update-state', 'update_state',
	'/api/get-state', 'get_state'
	)

# site pages

def notfound():
	return web.notfound(str(render.notfound()))

class index:		
	def GET(self):
		web.header('Cache-Control', 'no-store, no-cache, must-revalidate')
		web.header('Content-Type', 'text/html; charset=utf-8')
		return render.index()

# api pages

def set_api_headers():
	web.header('Cache-Control', 'no-store, no-cache, must-revalidate')
	web.header('Content-Type', 'application/json')

class get_session:
	def GET(self):
		set_api_headers()
		session_id = 0
		
		# find a session with the most players, but where players are less then 5 TODO
		sessions = db.select('sessions',  where='players < 5', order = 'players DESC')
		
		if (len(sessions) == 0):
			# sessions are all full, or we don't have any yet... create one
			newSession = openTokSDK.create_session(web.ctx.ip, {'echoSuppression_enabled': True})
			db.insert('sessions', session_id = newSession.session_id, players = 1, time_last_joined = datetime.now())
			session_id = newSession.session_id
		else:
			# there's a workable session, grab the first (most populous) one
			session = sessions[0];
			session_id = session.session_id

			#update the db to reflect what we will assume to be an additional player			
			db.update('sessions', where = "id = '" + str(session.id) + "'", players = session.players + 1, time_last_joined = datetime.now())
		
		# generate token
		token = openTokSDK.generate_token(session_id)		
		
		# pass the session and token back to the user
		return simplejson.dumps({'status': 'success', 'session_id': session_id, 'token': token})		
		
class update_session:
	def POST(self):
		set_api_headers()
		i = web.input(session = '', players = '')
		
		if i.players is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no player count'})
			
		if i.session is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no session id'})			
		
		# try to update the player count on the server
		change = db.update('sessions', where = "session_id = '" + i.session + "'", players = i.players, time_last_updated = datetime.now())
		
		# echo back to the user
		return simplejson.dumps({'status': 'success', 'players': i.players})


class update_state:
	def POST(self):
		set_api_headers()
		i = web.input(connection_id = '', running = '', color = '', bleach = '', speed = '')

		if i.connection_id is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no connection id'})

		if i.running is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no running boolean'})
			
		if i.color is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no color'})

		if i.bleach is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no bleach'})
			
		if i.speed is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no speed'})

		if i.running == 'true':
			i.running = 1
		else:
			i.running = 0

		# is there already an entry for this player?
		player = db.select('players',  where = "connection_id = '" + i.connection_id + "'")
		
		if len(player) is 0:
			# create a new entry
			db.insert('players', connection_id = i.connection_id, running = i.running, color = i.color, bleach = i.bleach, speed = i.speed, time_updated = datetime.now())
			return simplejson.dumps({'status': 'success', 'message': ('inserted player ' + i.connection_id)})
		else:
			# update the existing entry
			db.update('players', where = "connection_id = '" + i.connection_id + "'", running = i.running, color = i.color, bleach = i.bleach, speed = i.speed, time_updated = datetime.now())
			return simplejson.dumps({'status': 'success', 'message': ('updated player ' + i.connection_id)})
			
			
class get_state:
	def POST(self):
		set_api_headers()	
		connection_id = web.input(connection_id = '').connection_id
		
		if connection_id is '':		
			return simplejson.dumps({'status': 'error', 'message': 'no connection id'})		
		
		# is there already an entry for this player?
		players = db.select('players',  where = "connection_id = '" + connection_id + "'")
		
		if len(players) is 0:
			return simplejson.dumps({'status': 'error', 'message': 'no entry for that connection id'})		
		else:
			player = players[0]
		
			if player.running is 0:
				player.running = False
			else:
				player.running = True
			
			return simplejson.dumps({'status': 'success', 'connection_id': player.connection_id, 'running': player.running, 'color': player.color, 'bleach': player.bleach, 'speed': player.speed})

	
if __name__ == "__main__":
	app.run()
	
app = web.application(urls, globals(), autoreload=False) # ammended for mod_wsgi
app.notfound = notfound	
application = app.wsgifunc()