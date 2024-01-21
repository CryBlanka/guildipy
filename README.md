# Guildipy - Guilded x Spotify Integration

Guildipy is a Python script that integrates Guilded, with Spotify. It allows you to display your current Spotify listening status on your Guilded profile.

## Features

- Updates your Guilded status with the current track you are listening to on Spotify.
- Displays a custom emoji (Spotify emoji) on your Guilded profile to indicate your listening status.
- Built using Flask, asyncio, and Spotify API.

## Getting Started

### 1. Install Dependencies

```bash
pip install httpx spotipy Flask
```

### 2. Set Up Spotify API Credentials
- Create a Spotify Developer account and create a new application to obtain the client ID and client secret.
- Set the redirect URI to http://localhost:8888/callback.

### 3. Set Up Guilded Cookies
- Replace the placeholder values in the COOKIES dictionary with your Guilded account cookies.

You may use browser extenstion such as EditThisCookie to obtain your data.

### 4. Update Spotify API Credentials
Replace the placeholder values for **SPOTIPY_CLIENT_ID** and **SPOTIPY_CLIENT_SECRET** with your Spotify API credentials.

### 5. Run the Script
```bash
python guildi.py
```

### 6. Complete Spotify Authentication
Open your web browser and go to http://localhost:8888/callback to complete the Spotify authentication.

### 7. Enjoy Guildipy!
Your Guilded status will now be updated based on your Spotify listening activity.

### Customization
You can customize the script by modifying the values in the script, such as emoji ID, status messages, and more.

### Known Issues
- After getting timeout by Guilded the status stops updating.

If there are any issues with Guildipy accessing your Guilded account, double-check the provided cookies.

### Contributors
- [/u/blanka](https://www.guilded.gg/u/blanka)


### License
This project is licensed under the MIT License.
