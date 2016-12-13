# MusicRecommender
Uses the Facebook and Spotify APIs to show you recommended artists and your favourite genres.


HOW TO RUN THIS PROGRAM
First, make sure any modules are installed: requests, json, webbrowser, unittest
If you want to use my caches, make sure fb_music_cache.txt, spotify_search_cache.txt, and spotify_related_cache.txt 
  are in the same folder as 506_python.py.
If planning on using live data, open up 506_project.py and replace lines 37-38 with your client id and client secret from Spotify.

Then run python 506_project.py. Use the -u flag if you are on Git Bash.
Follow the prompts.
The first one gives you the option of using my Facebook cache or to get your Facebook data. 
As long as you don't type "mine", my Facebook cache will be used. If you do type "mine", 
  it will open the webbrowser for you to get your access token and paste it in.
Next, it should greet you, tell you your Facebook ID, and display the main menu.
Type 'A' to get recommended artists. 
Then type in any number. If you don't, it will ask you until you do. To get the output I have in top_bands.txt, type in 630 (or greater). 
My top recommended bands should display and the prompt should ask you if you want to save the file.
Type 'Y' to save a file. It will ask what you want to name the file. Choose a valid file name (no spaces, etc.) without the extension.
You should then see a txt file with this file name in your folder. Inside are the top recommended bands.
If you typed anything other than 'Y', it should have taken you to the next prompt.
Next, the prompt will ask if you want to listen to top recommended bands on YouTube. 
Type 'N' or anything that is not a valid number to skip this portion.
If you want to listen on YouTube, type any number, and your web browser should open with a tab for the top x recommended artists, 
  so keep this number low if you don't want a zillion tabs opening in your browser.
Next, it will take you back to the main menu.
Type 'B' to get top genres.
Then type in any number. If you don't, it will ask you until you do. To get the output I have in top_genres.txt, type in 114 (or greater).
My top genres should display and the prompt should ask you if you want to save the file.
Type 'Y' to save into a file. It will ask what you want to name the file. Choose a valid file name (no spaces, etc.) without the extension.
You should then see a txt file with this file name in your folder. Inside are the top genres.
You will be redirected to the main menu. Type Q to quit or use the other options to keep going.
After you type Q, my unit tests will run.

Note: there should be enough error handling / try blocks that you shouldn't have to worry too much about what you type in :)
The only things that are not handled are if you input an invalid Access Token, you don't have any music likes on Facebook, 
  or if you type in an invalid file name. If you find any things other than those that are not handled, feel free to let me know!
