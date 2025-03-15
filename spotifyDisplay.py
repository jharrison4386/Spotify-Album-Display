#Imports needed
import spotipy as spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.request as urllib
from PIL import Image
import os
import time
import numpy as np
import argparse
import cv2
import pygame
from pygame.locals import *
import requests
import json
from datetime import datetime,timedelta
import os.path

#Display image, vars needed, and spotify API needs
displayImage = "(Link or file path to image)"
songName=''
artist=''
temp = ''
weat = ''
scope = "user-read-currently-playing"
spotify_client_id = 'get from spotify dev account'
spotify_secret = 'get from spotify dev account'
spotify_redirect_uri = 'http://localhost:8888/callback'

results=''

#set up spotify API usage
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(spotify_client_id,
                    spotify_secret, spotify_redirect_uri, scope=scope))
                    
#Function to retrieve spotify song album cover and song info
def getAlbum(songName, artist):
    #global access to results
    global results
    #attempt every 5 seconds as to not rate limit API
    try:
        time.sleep(5)
        results = sp.current_user_playing_track()
    except Exception:
        pass
    #If no song playing, replace current display with blank screen
    if (results is None or results['item'] == None):
            windowSurface.fill((0,0,0), rect = (640,100,1280,1080))
            imgBlack = cv2.imread('black.png')
            cv2.imwrite('tempCover.png',imgBlack)
            return ' ',' '
    #Gather song info
    else:
        song=results['item']['name']
        art = results['item']['album']['artists'][0]['name']
    if (len(results['item']['album']['images']) == 0):
        #If song has no album cover, use this image instead
        albumCover = "insert link or path to sample album cover"
    else:
            albumCover=results['item']['album']['images'][0]['url']
    #Check if song has changed by comparing new song name, grab new album cover
    if (songName != song):
        gfg, headers = urllib.urlretrieve(albumCover)
        songName = song
        artist = art

        img = cv2.imread(gfg)
        cv2.imwrite("tempCover.png",img)
        windowSurface.fill((0,0,0))
        return songName, artist
    #If not new, keep same
    else:
        songName = songName
        artist = artist
        return songName, artist
        
#Use NWS API to get weather info for current area        
def getWeather():
    link = "https://api.weather.gov/gridpoints/HGX/29,134/forecast/hourly"
    forecast = requests.get(link)
    try:
        temp = forecast.json()['properties']['periods'][0]['temperature']
        weather = forecast.json()['properties']['periods'][0]['shortForecast']
    except (KeyError, requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError):
        temp = 'error'
        weather = 'error'
    return temp, weather
    
#keep display monitor from turning off    
os.system("xset s noblank")
os.system("xset -dpms")
os.system("xset s off")

#Create Display window
pygame.init()
width = 1920
height = 1080
windowSurface = pygame.display.set_mode((width, height), 32, pygame.NOFRAME)

os.environ["SDL_VIDEO_CENTERED"] = '1'

#Looping through to constantly update display image weather,song, and time
while True:
    pygame.font.init()
    
    #Creating fonts for display text
    fontName = '/usr/share/fonts/truetype/circularblack/Circular-Std-Black.ttf'
    my_font = pygame.font.SysFont(fontName, 45)
    time_font = pygame.font.SysFont('Arial', 50)
    
    #Exit protocol
    events = pygame.event.get()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    #If it is between midnight and 8am, turn monitor off
    if 0 <= int(str(datetime.now())[12]) < 8 and int(str(datetime.now())[11]) == 0:
        os.system("vcgencmd display_power 0")
    #If not between 12am or 8am, update monitor images
    else:
        os.system("vcgencmd display_power 1")
        with open('message.txt', 'r') as file:
            #Read message delivered via telegram bot and written to file
            messageSent = file.read()
        windowSurface.fill((0,0,0))
        
        #Get song info and weather info
        songName, artist = getAlbum(songName, artist)
        temp, weat = getWeather()
        
        #Render message as text and fit to screen
        textMessage = time_font.render(messageSent, True, (230,31,134))
        windowSurface.blit(textMessage, (50, 900))
        windowSurface.blit(pygame.image.load("tempCover.png"), (640,100))
        
        #Song text info
        text = my_font.render(songName, True, (255,255,255))
        textArtist = my_font.render(artist, True, (255,255,255))
        
        #Time display text
        t = datetime.strptime(str(datetime.now())[11:16], "%H:%M")
        t = t.strftime("%I:%M %p")
        textTime = time_font.render(t, True, (230,31,134))
        textDate = time_font.render(str(datetime.now())[5:10], True, (230,31,134))
        
        #Weather text
        textTemp = time_font.render(f"{temp}°", False, (230,31,134))
        textWeat = time_font.render(weat, True, (230,31,134))
        width, height = my_font.size(str(songName))
        
        #Get width and height of current text as it changes to determine where to put text
        widthTime, heightTime = time_font.size(str(textTime))
        widthDate, heightDate = time_font.size(str(textDate))
        widthArtist, heightArtist = my_font.size(str(artist))
        widthWeat, heightWeat = time_font.size(weat)
        widthTemp, heightTemp = time_font.size(str(textTemp))
        
        #Apply texts to current display
        windowSurface.blit(text, (640+(320-width/2), 825))
        windowSurface.blit(textArtist, (640+(320-widthArtist/2), 875))
        windowSurface.fill((0,0,0), rect = (50,50,300,200))
        windowSurface.blit(textTime, (50, 50))
        windowSurface.blit(textDate, (50+((widthTime-widthDate)/2), 100))
        windowSurface.blit(pygame.image.load("kitty.jpg"), (1380,350))
        windowSurface.blit(textTemp, ((1915-widthWeat),50))
        windowSurface.blit(textWeat, ((1915-widthWeat),100))
        
        #Update display all at once
        pygame.display.flip()
