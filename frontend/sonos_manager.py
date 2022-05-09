import datastore
import threading
import time
import json
import soco
from soco import *


device = SoCo("192.168.5.166")

DATASTORE = datastore.Datastore()

pageSize = 50
has_internet = False

def check_internet(request):
	global has_internet
	try:
		result = request()
		has_internet = True
	except Exception as _:
		result = None
		has_internet = True
	return result

def get_now_playing():
	response = check_internet(lambda: sp.current_playback(additional_types='episode'))
	if (not response):
		return get_now_playing_track()

	if (response['currently_playing_type'] == 'episode'):
		return get_now_playing_track()
	else:
		return get_now_playing_track()

def get_now_playing_track():
	now_playing = {
		'title': device.get_current_track_info()['title'],
		'artist': device.get_current_track_info()['artist'],
		'album': device.get_current_track_info()['album'],
		'is_playing': device.get_current_transport_info()['current_transport_state']
	}
	return now_playing

def get_now_playing_episode(response = None):
	if(not response or not response['item']):
		return None

	episode = response['item']
	episode_uri = episode['uri']
	publisher = episode['show']['publisher']
	now_playing = {
		'name': episode['name'],
		'track_uri': episode_uri,
		'artist': publisher,
		'album': episode['show']['name'],
		'duration': episode['duration_ms'],
		'PLAYING': response['PLAYING'],
		'progress': response['progress_ms'],
		'context_name': publisher,
		'track_index': -1,
		'timestamp': time.time()
	}
	
	return now_playing

def refresh_now_playing():
	DATASTORE.now_playing = get_now_playing()

def play_next():
	global sleep_time
	device.next()
	sleep_time = 0.4
	refresh_now_playing()

def play_previous():
	global sleep_time
	device.previous()
	sleep_time = 0.4
	refresh_now_playing()

def pause():
	global sleep_time
	device.pause()
	sleep_time = 0.4
	refresh_now_playing()

def resume():
	global sleep_time
	device.play()
	sleep_time = 0.4
	refresh_now_playing()

def toggle_play():
	now_playing = device.get_current_transport_info()['current_transport_state']
	if now_playing == 'PLAYING':
		pause()
	elif now_playing == 'PAUSED_PLAYBACK':
		resume()
	else:
		return

def bg_loop():
	global sleep_time
	while True:
		refresh_now_playing()
		time.sleep(sleep_time)
		sleep_time = min(4, sleep_time * 2)

sleep_time = 0.3
thread = threading.Thread(target=bg_loop, args=())
thread.daemon = True                            # Daemonize thread
thread.start()

def run_async(fun):
	threading.Thread(target=fun, args=()).start()
