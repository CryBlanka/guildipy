import httpx
import json
import time
import io
import requests
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request
from threading import Thread
import asyncio
import sys

# Your Guilded cookies
COOKIES = {
    'guilded_mid': '', # Change to your own guilded_mid
    'hmac_signed_session': '', # Change to your own hmac_signed_session
    'authenticated': 'true',
    'guilded_ipah': '', # Change to your own guilded_ipah
    'gk': 'native_reaction_rotating_count%2Cnative_disable_response_check_before_parse_json%2Cshare_channel_content_on_native%2Cenable_video_overlay_v2%2Cenable_action_menu_v2%2Cenable_android_maintain_scroll_position%2Cenable_mark_all_activities_as_read%2Cdisable_rtc_websocket%2Cuser_socket_channel_rooms%2Cenable_can_create_chat_forms_permission%2Cheartbeat_in_rtc_connection%2Cextra_rtc_logging%2Cemit_events_over_data_channel%2Cenable_tab_filter_overlay%2Cenable_members_sidebar_drawer_v2%2Cenable_notification_reply_action%2Cenable_regex_link_validation%2Cvoice_input_preference_list%2Crefresh_voice_consumers_on_join%2Cvoice_use_data_channel_events%2Candroid_callkeep_disabled%2Cenable_zoomable_image_v2%2Cenable_insert_gif_picker_v2%2Cenable_private_events%2Cenable_image_overlay_v2%2Cnative_rich_content_reaction_fix%2Cenable_form_export_to_csv%2Cdrawer_v2%2Cenable_editor_toolbar_overlay%2Casync_team_member_management%2Cmultiple_files_drag_drop%2Cshow_ptt_warning_banner%2Cnative_reaction_motion%2Cenable_async_reactions%2Cnative_emotes_settings_screen%2Cserver_subs_prevent_native_subscribe_flow_ios%2Cenable_remove_reactions%2Cgame_overlay%2Cmentionables_v2%2Cprofile_hover_card_v3%2Cdrawbridge%2Cshow_game_presence%2Cnative_update_app_overlay',
}

# Guildipy ascii art & info
GUILDIPY_ART = '''
   _____       _ _     _ _             
  / ____|     (_) |   | (_)            
 | |  __ _   _ _| | __| |_ _ __  _   _ 
 | | |_ | | | | | |/ _` | | '_ \| | | |
 | |__| | |_| | | | (_| | | |_) | |_| |
  \_____|\__,_|_|_|\__,_|_| .__/ \__, |
                          | |     __/ |
                          |_|    |___/ 
\n'''
GUILDIPY_INFO = 'Guildipy, a Guilded x Spotify integration. Made with love by Blanka 💜\n'
GUILDIPY_ERROR_LOGIN = 'Guildipy was unable to access your Guilded account, please check the cookies.'
GUILDIPY_ERROR_UNKNOWN = 'Guildipy found an unknown error.'
GUILDIPY_CURRENT_STATUS_NONE = 'Not currently playing'
GUILDIPY_CURRENT_STATUS_PAUSED = 'Not currently playing (Paused)'
GUILDIPY_CURRENT_STATUS_ACTIVE = 'Listening'
GUILDIPY_EMOTE_ID = 2211233 # Default Spotify emoji id.
GUILDIPY_CALLBACK_TEXT = 'Callback received! You can close this window.'

# Spotify API credentials
SPOTIPY_CLIENT_ID = '' # Change to your Spotify client id.
SPOTIPY_CLIENT_SECRET = '' # Change to your Spotify client secret.
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Flask setup
app = Flask(__name__)
callback_data = None

# Spotify API authentication
sp_oauth = SpotifyOAuth(
    SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET,
    SPOTIPY_REDIRECT_URI,
    scope='user-read-currently-playing',
)
sp = Spotify(auth_manager=sp_oauth)


class SpotifyApp:
    def __init__(self):
        self.current_track_info = None
        print(GUILDIPY_ART, GUILDIPY_INFO)
        self.start_flask()

    def get_track_info(self):
        try:
            current_track = sp.current_user_playing_track()
            if current_track is not None and 'item' in current_track:
                track_name = current_track['item']['name']
                artist_name = current_track['item']['artists'][0]['name']
                is_playing = current_track['is_playing']

                if is_playing:
                    if track_name and artist_name:
                        return f'{GUILDIPY_CURRENT_STATUS_ACTIVE} to {track_name} by {artist_name}'
                    else:
                        return GUILDIPY_CURRENT_STATUS_NONE
                else:
                    return GUILDIPY_CURRENT_STATUS_PAUSED
            else:
                return GUILDIPY_CURRENT_STATUS_NONE
        except Exception as e:
            print(f"Error: {e}")
            return GUILDIPY_ERROR_UNKNOWN

    async def update_presence(self):
        while True:
            new_track_info = self.get_track_info()

            if new_track_info != self.current_track_info:
                self.current_track_info = new_track_info
                update_guilded_status(new_track_info)

            await asyncio.sleep(2)

    def update_gui(self):
        asyncio.create_task(self.update_presence())

    def start_flask(self):
        thread = Thread(target=run_flask)
        thread.start()

def update_guilded_status(current_status):
    # Set your status payload
    status_content = {'object': 'value', 'document': {'object': 'document', 'data': {}, 'nodes': [{'object': 'block', 'type': 'paragraph', 'data': {}, 'nodes': [{'object': 'text', 'text': f'{current_status}'}]}]}}
    custom_reaction_id = GUILDIPY_EMOTE_ID
    expire_in_ms = 0

    status_data = {
        'content': status_content,
        'customReactionId': custom_reaction_id,
        'expireInMs': expire_in_ms
    }

    status_url = 'https://www.guilded.gg/api/users/me/status'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,en-US;q=0.6',
        'Content-Type': 'application/json',
        'Cookie': '; '.join([f'{key}={value}' for key, value in COOKIES.items()]),
        'Guilded-Client-Id': 'fef403f5-90b5-4c71-9d96-a89f9a0148ab',
        'Guilded-Viewer-Platform': 'desktop',
        'Origin': 'https://www.guilded.gg',
        'Referer': 'https://www.guilded.gg/Clippsly',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        response = httpx.post(status_url, headers=headers, json=status_data)
        
    except httpx.RequestError as e:
        return GUILDIPY_ERROR_LOGIN

@app.route('/callback')
def callback():
    global callback_data
    callback_data = request.args

    return GUILDIPY_CALLBACK_TEXT

def run_flask():
    sys.stdout = open(".flask-guildipy", "w")
    sys.stderr = open(".flask-guildipy", "w")
    app.run(port=8888, use_reloader=False, debug=False)

if __name__ == '__main__':
    spotify_app = SpotifyApp()
    while True:
        asyncio.run(spotify_app.update_presence())
