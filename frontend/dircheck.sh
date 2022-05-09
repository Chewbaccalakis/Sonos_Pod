export SPOTIPY_CLIENT_ID='5816057a8bab4611bbbb3cc1c2bca6fa'

export SPOTIPY_CLIENT_SECRET='6b90ce2503da4becbd66fc3ea000b01b'

export SPOTIPY_REDIRECT_URI='http://127.0.0.1'

sudo -H -u nick --preserve-env=SPOTIPY_REDIRECT_URI,SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET python3 spotifypod.py &