
import alsaaudio
import subprocess
import flask 
import webbrowser 
from alsaaudio import Mixer
from subprocess import call 
from flask import Flask
from flask import json
from flask import request

# Index (acording to ALSA) of the sound card you
# wish to manage see 
# `cat /proc/asound/cards` for a list
SOUND_CARD = 0
# The 'Mixer' that will be used to adjust the volume  
# `amixer -c <SOUND_CARD> scontrols` for a list
# where the <SOUND_CARD> is the index of your sound card
SOUND_MIXER = 'Master'


app = Flask(__name__)

#----------------------------------------------------------
#-------- OPEN URL ----------------------------------------
# Open the given URL in the system default browser 
# { value: 'http://google.com.au' }
#----------------------------------------------------------
@app.route('/open/url', methods=['POST'])
def open_url(): 
	app.logger.debug('Open URL Request')
	
	if request.json is None: 
		return flask.jsonify(error='Invalid JSON request')
	 
	url = request.json['value']
	
	webbrowser.open_new_tab(url)
	return flask.jsonify(success='Opened URL')


#----------------------------------------------------------
#-------- VOLUME ------------------------------------------
# Get or set the current volume 
#----------------------------------------------------------
@app.route('/volume', methods=['GET', 'POST'])
def volume(): 
	app.logger.debug('Volume Request ')
	app.logger.debug(request.json)
	
	# GET the current volume 
	if 'GET' == request.method: 
		return flask.jsonify(value=get_volume(), units='%')

	# POST the new volume value 	
	if 'POST' == request.method: 
		if request.json is None: 
			return flask.jsonify(error='Invalid JSON Request')

		value = request.json['value']
		action = request.json['action'] # one of 'set' 'increase' 'decrease' 

		if value < 0 or value > 100: 
			return flask.jsonify(error='Volume is not in range of 0 - 100')

		if action not in ['set', 'increase', 'decrease']:
			return flask.jsonify(error='action invalid')
		
		if action in ['increase', 'decrease']: 
			current_volume = get_volume()
			app.logger.info('Current Volume is ' + str(current_volume))

			if action == 'increase': 
				value = current_volume + value
				if value > 100: 
					value = 100
			if action == 'decrease':
				value = current_volume - value 
				if value < 0: 
					value = 0

		set_volume(value)
		return flask.jsonify(success='Volume set to ' + str(value) + '%')


def get_volume():
	id = alsaaudio.mixers(SOUND_CARD).index(SOUND_MIXER)
	mixer = Mixer(SOUND_MIXER, id, SOUND_CARD)
	return mixer.getvolume()[0]


def set_volume(val):
	id = alsaaudio.mixers(SOUND_CARD).index(SOUND_MIXER)
	mixer = Mixer(SOUND_MIXER, id, SOUND_CARD)
	mixer.setvolume(val)


#----------------------------------------------------------
#-------- MAIN --------------------------------------------
#
if __name__ == '__main__': 

	# DEBUG 
	# Listen on all public IP addresses in debug mode 
	app.run(host='0.0.0.0', debug=True, port=5000)

	# Run in debug mode 
	#app.run(debug=True)

	# Run in production mode 
	#app.run()

