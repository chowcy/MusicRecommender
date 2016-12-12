# SI 506 Final Project
# Coded by Cathy Chow, 2016.

import requests
import json
import unittest
import webbrowser
from pprint import pprint


##############VARIABLES FOR FACEBOOK REQUESTS#######################

#Paste your access token here if cache doesn't work. Make sure you have user.likes selected
#Make sure you have at least one musician liked on Facebook. I didn't check what happens if you don't.
fb_access_token = ''
fb_base_url = "https://graph.facebook.com/v2.8/me"
fb_params_dict = {}
fb_params_dict['access_token'] = fb_access_token
fb_params_dict['fields'] = 'music, name, id'

fb_cache_fname = "fb_music_cache.txt"
spot_artist_cache_fname = "spotify_search_cache.txt"
spot_related_cache_fname = 'spotify_related_cache.txt'

##############VARIABLES FOR SPOTIFY REQUESTS#########################


##For searching the artist: no oauth needed
base_url_search = 'https://api.spotify.com/v1/search'
param_search_dict = {}
param_search_dict['type'] = 'artist'


##For requesting info that requires authorization, such as related artists
#Gets Access Token
#Paste your client_id and client_secret if you don't want to use mine
client_id = ''
client_secret = ''
base_url_token = 'https://accounts.spotify.com/api/token'
param_token_dict = {'grant_type' : 'client_credentials'}


##For getting related artists
#Request url is in this format: 'https://api.spotify.com/v1/artists/' + artist_id + '/related-artists'
base_url_related = 'https://api.spotify.com/v1/artists/'


class FacebookUser():

	def __init__(self, fb_data):
		self.user_id = fb_data['id']
		self.user_name = fb_data['name']

		#list of names of artists liked on facebook. Will be filtered when making Artist objects
		self.list_artists = [artist['name'] for artist in fb_data['music']['data']]

	def __str__(self):
		return self.user_name

	def get_Artist_list(self, artist_data_dict):
		'''
			REQUIRES: dictionary of liked artists' data from Spotify
			EFFECTS: returns list of Artist objects only for each artist the user likes that has Spotify data
		'''

		return [ Artist(artist_data_dict[artist]) for artist in artist_data_dict ]

	def top_related_artists(self, artist_data_dict, related_artist_data):
		'''
		REQUIRES: dictionary of  liked artists' data from Spotify
		dictionary of the related artists of those artists (so it can be passed into the Artist constructor)
		EFFECTS:  returns list of all related artists for all users' liked artists, sorted from most frequent to least
		'''

		freq_dict = {}
		Artist_list = self.get_Artist_list(artist_data_dict)
		for artist in Artist_list:
			#if manage to get related artists for that artist
			if artist.get_related_artists(related_artist_data) != None: 
				#for each related artist in the Artist list
				for related_artist in artist.get_related_artists(related_artist_data):

					#only include recommendations for artists that the user does not already like
					if related_artist.artist_name not in [artist.artist_name for artist in Artist_list]:

						#put into dictionary
						if related_artist.artist_name in freq_dict:
							freq_dict[related_artist.artist_name] += 1
						else:
							freq_dict[related_artist.artist_name] = 1
		alphabetized = sorted(freq_dict.items(), key = lambda (x, y) : x.upper())
		return [ freq for freq in sorted(alphabetized, key = lambda (x, y): y, reverse = True) ]

	def top_genres(self, artist_data_dict):
		'''
		REQUIRES: dictionary of liked artists' data from Spotify
		EFFECTS:  returns list of all genres for all users' liked artists, sorted from most frequent to least
		'''
		freq_dict = {}
		Artist_list = self.get_Artist_list(artist_data_dict)
		for artist in Artist_list:
			if len(artist.genres) > 0: 
				for genre in artist.genres:
					if genre in freq_dict:
						freq_dict[genre] += 1
					else:
						freq_dict[genre] = 1
		alphabetized = sorted(freq_dict.items(), key = lambda (x, y) : x.upper())
		return [ freq for freq in sorted(alphabetized, key = lambda (x, y): y, reverse = True) ]

class Artist():
	def __init__(self, artist_data):
		self.artist_name = artist_data['name'].encode('utf-8')
		self.genres = artist_data['genres']
		self.artist_id = artist_data['id']

	def __str__(self):
		return self.artist_name

	def get_related_artists(self, related_artist_data):
		'''
		REQUIRES: a dictionary that has information on related artists for artists
		EFFECTS: returns a list of Artist objects for each related artist that has data in the dictionary passed in. 
		'''
		#there may be artists that we could find searches for, but which have no related artists.
		#if no related artists were found, will go to except block and return None
		try:
			related_artists = related_artist_data[self.artist_id]
			#if related artists exist, return related artists list
			return [ Artist(artist) for artist in related_artists ]
		except: 
			pass

def print_menu(menu_type, limit = 100):
	'''
		REQUIRES: a menu type to specify which menu to print
		EFFECTS: prints the correct menu depending on menu_type, prints a limit if the user needs to know that in the menu
	'''
	print '*************************************'
	if menu_type == 'live data':
		print "Would you like to use your Facebook data or Cathy's Facebook cached data?"
		print "In order to use your Facebook data, you must have some musicians/bands liked."
		print '===========Options=========='
		print "mine: Use your Facebook data. (Requires internet connection.)"
		print "cache: Use Cathy's cache. (default)"
	elif menu_type == "access token":
		print 'I will need your Facebook user access token.'
		webbrowser.open('https://developers.facebook.com/tools/explorer/')
		print 'Please select "Get Token" -> "Get User Access Token", and check "user_likes".'
		print 'Then press "Get Access Token."'
		print 'A window may prompt you to log in. If it does, log in.'
		print 'Your access token should now appear. It is a long sequence of letters and numbers.'
		print 'Please paste this access token into the command line window.'
	elif menu_type == 'start':
		print 'What would you like to do?'
		print '===========Options=========='
		print 'A: Get top recommended artists.'
		print 'B: Get your top genres.'
		print 'Q: Quit this program.'
		print 
	elif menu_type == 'top related':
		print 'How many recommended artists would you like to output?'
		print 'Cannot exceed ' + str(limit) + ' artists.'
	elif menu_type == 'write to file':
		print 'Would you like to write this to a .txt file?'
		print '===========Options=========='
		print 'Y: yes'
		print 'N: no (default)'
	elif menu_type == 'youtube':
		print 'Would you like to listen to some of these artists on YouTube?'
		print 'This will open a tab on your web browser for each artist on YouTube, so you must have an internet connection.'
		print '===========Options=========='
		print 'N: no (default)'
		print 'If yes, type how many artists you would to listen to on YouTube.'
		print 'Cannot exceed ' + str(limit) + ' artists.'
	elif menu_type == 'genres':
		print 'How many top genres would you like to output?'
		print 'Cannot exceed ' + str(limit) + ' genres.'

def put_in_range(num, minimum, maximum):

	'''
	REQUIRES: three numbers. 
	EFFECTS: returns the number if it is between the minimum and maximum, 
				returns the maximum if the number exceeds the maximum,
				returns the minimum if the number is lower than the maximum.
	'''
	if num > maximum:
		return maximum
	elif num < minimum:
		return minimum
	return num

def interaction_driver(user, spotify_artist_info, spotify_related_info):
	'''
	REQUIRES: a FacebookUser object, a dictionary of that user's liked artists' spotify information, a dictionary of related artist information for each liked artist
	EFFECTS: runs the main program with the user, which can:
			print top recommended artists in command line
			save this to a file
			open a youtube page for recommended artists
			print user's top genres
			save this to a file
	'''
	print_menu('start')
	user_input = raw_input()
	while user_input != 'Q':
		if user_input == 'A':

			#print top recommendations depending on how many they want
			top_recs = user.top_related_artists(spotify_artist_info, spotify_related_info)
			print_menu('top related', len(top_recs))

			try:
				#will fail if a non-number was inputted
				num_recs = int(raw_input())

			except:
				invalid = True
				while invalid:
					try: 
						num_recs = int(raw_input('Please enter a valid number.'))
						invalid = False
					except:
						pass
			#handle numbers not in range
			num_recs = put_in_range(num_recs, 0, len(top_recs))

			#this variable is for the number that prints next to the artist
			store_rank_number = 1

			#print the artists. top_recs[i][0] denotes the name of the artist
			for i in range(num_recs):
				#if band has same frequency as another, this number will show that those with equal ranking have the same number
				if i != 0 and top_recs[i][1] != top_recs[i - 1][1]:
					store_rank_number += 1
				print store_rank_number, top_recs[i][0]

			if num_recs > 0:
				#ask if they'd like this information saved to a file
				print_menu('write to file')
				to_write = raw_input()
				if to_write == 'Y':
					file_name = raw_input('Please enter a valid file name without the .txt extension. ')
					f = open(file_name + '.txt', 'w')

					#write to file
					store_rank_number = 1
					for i in range(num_recs):
						if i != 0 and top_recs[i][1] != top_recs[i - 1][1]:
							store_rank_number += 1
						f.write(str(store_rank_number))
						f.write(' ')
						f.write(top_recs[i][0])
						f.write('\n')

					f.close()

			#ask if they'd like to listen to this artist on YouTube
			#will open web browser depending on how many artists they want to listen to
			print_menu('youtube', len(top_recs))
			num_youtube = raw_input()
			try:
				#will fail if a non-number was inputted. Meaning No.
				num_youtube = int(num_youtube)

			#in case numbers are out of range
				num_youtube	= put_in_range(num_youtube, 0, len(top_recs))		
				for artist in top_recs[:num_youtube]:
					youtube_url = 'https://www.youtube.com/results?search_query=' + artist[0] + ' Music' + '&page=&utm_source=opensearch'
					webbrowser.open(youtube_url)

			except:
				pass
			

		elif user_input == 'B':
			#print top genres depending on how many they want
			top_genres = user.top_genres(spotify_artist_info)
			print_menu('genres', len(top_genres))
			num_genres = int(raw_input())

			#in case numbers are out of range
			num_genres = put_in_range(num_genres, 0, len(top_genres))

			#this variable is for the number that prints next to the artist
			store_rank_number = 1

			#print the genres. top_genres[i][0] denotes the name of the genre
			for i in range(num_genres):
				#if genre has same frequency as another, this number will show that those with equal ranking have the same number
				if i != 0 and top_genres[i][1] != top_genres[i - 1][1]:
					store_rank_number += 1
				print store_rank_number, top_genres[i][0]

			if num_genres > 0:
				#ask if they'd like this information saved to a file
				print_menu('write to file')
				to_write = raw_input()
				if to_write == 'Y':
					file_name = raw_input('Please enter a valid file name without the .txt extension. ')
					f = open(file_name + '.txt', 'w')

					#write to file
					store_rank_number = 1
					for i in range(num_genres):
						if i != 0 and top_genres[i][1] != top_genres[i - 1][1]:
							store_rank_number += 1
						f.write(str(store_rank_number))
						f.write(' ')
						f.write(top_genres[i][0])
						f.write('\n')

					f.close()


		else:
			print 'Invalid input. Please type either the letter A, B, or Q.'

		#reenter loop	
		print_menu('start')
		user_input = raw_input()

	#User typed Q
	print 'Goodbye!'

#############GET FACEBOOK DATA AND CACHE###############################
def get_facebook_data(fb_access_token = fb_access_token, fb_cache_fname = fb_cache_fname):
	'''
	REQUIRES: the global variable fb_cache_fname is a valid file name
	EFFECTS: makes request to Facebook API or uses Cache to get a dictionary of information on the users' liked artists
	'''
	fb_cache = {}
	try:
		#if a cache file exists, use it
		#if the file exists, the program will use what's inside it, so make sure it is 
		#if following line fails, probably because the file does not exist
		f = open(fb_cache_fname, 'r')
		fb_data = json.loads(f.read())
		f.close()
		print 'Getting data from Facebook Cache'

	except: 
		#if file does not exist
		print 'Getting data from Facebook API'
		fb_params_dict['access_token'] = fb_access_token
		fb_response = requests.get(fb_base_url, params= fb_params_dict)
		fb_data = fb_response.json()

		is_more = True
		#check if need to do paging
		try:
			next_url = fb_data['music']['paging']['next']
		except KeyError as e:
			#invalid oauth
			if e.message == 'music':
				print fb_access_token
				print 'Invalid Oauth. Either expired or empty. Please get a fresh token from Facebook.'
				print 'Alternatively, you have no Music likes on Facebook'
			elif e.message == 'next':
				#there is no next page
				#e.message would be 'next' in this case
				print 'No next page'
				is_more	= False
			else:
				print 'unexpected error!'

			#need to do paging to get the rest of the artist

		while is_more:
			# try:
			fb_request = requests.get(next_url)
			fb_response_ = fb_request.json()
			fb_data['music']['data'] += fb_response_['data']

			#get next url. if next is missing, means there are no more pages and will skip to exception
			try:
				next_url = fb_response_['paging']['next']
			except KeyError:
				print 'No more paging in Facebook'
				is_more = False

		##Cache the data
		f = open(fb_cache_fname, 'w')
		f.write(json.dumps(fb_data))
		f.close()
	return fb_data

##############################GET SPOTIFY SEARCH AND CACHE#######################################
def run_spotify_search(User):
	#dict for storing results of searches
	spotify_search_cache = {}
	#dict for storing data on Artists user likes that return search results 
	spotify_artist_info = {}

	#Check whether spotify cache file has been created
	try:
		f = open(spot_artist_cache_fname, 'r')
		spotify_search_cache = json.loads(f.read())
		f.close()
	except:
		print 'no spotify search cache found'

	#goes through list of artists and caches if not found in cache
	for artist_name in User.list_artists:
		#artist name has been searched and is in cache
		try: 
			#if the artist is in the cache, just pull the value from the cache
			if spotify_search_cache[artist_name] != 'none':
				spotify_artist_info[artist_name] = spotify_search_cache[artist_name]

		#artist name has not been searched for
		except KeyError as e:

			print 'Making search request to Spotify API'
			param_search_dict['q'] = artist_name
			search_response = requests.get(base_url_search, params = param_search_dict)
			artist_search_data = search_response.json()	

			#if at least one artist is returned from search results
			if artist_search_data['artists']['total'] > 0:
				#index 0 to get the first/top search result
				artist_info = artist_search_data['artists']['items'][0]
				#add to cache
				spotify_search_cache[artist_name] = artist_info
				#add to our data structure
				spotify_artist_info[artist_name] = artist_info

			#no search results found :(
			else:
				print 'No search results found for ' + artist_name
				print 'Removing ' + artist_name + ' from analysis'
				#note that in cache, there are no results
				spotify_search_cache[artist_name] = 'none'

	f = open(spot_artist_cache_fname, 'w')
	f.write(json.dumps(spotify_search_cache))
	f.close()

	return spotify_artist_info

#######################GET SPOTIFY RELATED ARTISTS AND CACHE#########################################

def request_spotify_related(User, spotify_artist_info):
	#dict for storing results of related artists
	spotify_related_cache = {}
	spotify_related_info = {}

	#Check whether spotify cache file has been created
	try:
		f = open(spot_related_cache_fname, 'r')
		spotify_related_cache = json.loads(f.read())
		f.close()
	except:
		print 'no spotify related artists cache found'

	#goes through list of artists and caches if not found in cache
	for artist in User.get_Artist_list(spotify_artist_info):
		#artist name has been found and is in cache
		try: 
			if spotify_related_cache[artist.artist_id] != 'none':
				spotify_related_info[artist.artist_id] = spotify_related_cache[artist.artist_id]

		#related artists have not been searched for
		except KeyError as e:

			print 'Making related artists request to Spotify API'
			token_response = requests.post(base_url_token, data = param_token_dict, auth = (client_id, client_secret))
			token_dict = token_response.json()
			try:
				access_token = token_dict['access_token']
			except:
				print 'Probably invalid client id and client secret!!!'
			header_dict_token = {'Authorization': ('Bearer ' + access_token)}
			param_search_dict['id'] = artist.artist_id
			related_response = requests.get((base_url_related + artist.artist_id + '/related-artists'), headers = header_dict_token)
			artist_related_data = related_response.json()	

			#if at least one artist is returned from related results
			if len(artist_related_data['artists']) > 0:
				spotify_related_info[artist.artist_id] = artist_related_data['artists']
				spotify_related_cache[artist.artist_id] = artist_related_data['artists']

			#no search results found :(
			else:
				print 'No related artists found for ' + artist.artist_name
				print 'Removing', artist, 'from analysis'
				spotify_related_cache[artist.artist_id] = 'none'

	f = open(spot_related_cache_fname, 'w')
	f.write(json.dumps(spotify_related_cache))
	f.close()

	return spotify_related_info
#########################################START OF PROGRAM##################################################

print "Hello! Welcome to Cathy's Music Recommendation Program!"

#Ask whether user wants to use own data or cached data
print_menu('live data')
live = raw_input()

#Ask for their access token if they want to use their own data
if live == 'mine':
	print_menu('access token')
	fb_access_token = raw_input()
	fb_user_data = get_facebook_data(fb_access_token = fb_access_token, fb_cache_fname = 'my_fb_music_cache.txt')
else:
	fb_user_data = get_facebook_data()

# print 'Creating Facebook User instance'
User = FacebookUser(fb_user_data)

# print 'Getting Spotify search data'
spotify_artist_info = run_spotify_search(User)

# print 'Getting Spotify related artist data'
spotify_related_info = request_spotify_related(User, spotify_artist_info)

print 'Starting main driver...'
print 'Hello',
print User
interaction_driver(User, spotify_artist_info, spotify_related_info)

#UNIT TESTS 
sample_fb_data = {"music": {
					 "data": [
					 {"created_time": "2016-12-03T17:49:10+0000", "name": "Passion Pit", "id": "63224190085"}, 
					 {"created_time": "2016-12-03T17:48:07+0000", "name": "Deafheaven", "id": "152244168212417"}, 
					 {"created_time": "2016-12-03T17:46:41+0000", "name": "Xerath", "id": "33434396077"}, 
					 {"created_time": "2016-12-03T17:46:11+0000", "name": "The Faceless", "id": "200878716073"} ] }, 
				"name": "Test User", 
				"id": "10153037726223192" } 
me = FacebookUser(sample_fb_data)

#will use my cache to look up artists
my_spotify_artists = run_spotify_search(me)
my_spotify_related = request_spotify_related(me, my_spotify_artists)
my_Artist_list = me.get_Artist_list(my_spotify_artists)


test_artist = {
'name': 'sample name',
'id': 'sample id',
'genres': ['rock', 'pop', 'jazz']
}
the_faceless_data = {
'name': 'The Faceless',
'id': "1FQ6uth7icR6Jhla16K2vC",
'genres': ["brutal death metal", "death core", "death metal", "deathgrind", "djent", "jazz metal", "mathcore", "melodic metalcore", "metalcore", "technical death metal"]
}
the_faceless = Artist(the_faceless_data)

class FacebookUserClass(unittest.TestCase):

	def test_name(self):
		self.assertEqual(me.user_name, 'Test User', "testing facebook user's name") 
	def test_id(self):
		self.assertEqual(me.user_id, '10153037726223192', "testing facebook user's id #") 
	def test_list_artists1(self):
		self.assertEqual(me.list_artists[0], 'Passion Pit', "testing facebook user's first music like")
	def test_list_artists2(self):
		self.assertEqual(me.list_artists[-1], 'The Faceless', "testing facebook user's last music like")

class ArtistClass(unittest.TestCase):

	def test_name(self):
		self.assertEqual(Artist(test_artist).artist_name, 'sample name', "testing whether name correct")		
	def test_id(self):
		self.assertEqual(Artist(test_artist).artist_id, 'sample id', "testing whether id correct")
	def test_genres(self):
		self.assertEqual(Artist(test_artist).genres, ['rock', 'pop', 'jazz'], "testing whether genres correct")

#Artist_list's order changes so can't assertEqual my_Artist_list[0].artist_name. using assertIn instead
class GetArtistList(unittest.TestCase):
	def test_length(self):
		self.assertEqual(len(my_Artist_list), 4, "testing whether length of list is correct")
	def test_Name1(self):
		self.assertIn("Passion Pit", [i.artist_name for i in my_Artist_list], "testing whether name is in list")		
	def test_id1(self):
		self.assertIn('7gjAu1qr5C2grXeQFFOGeh', [i.artist_id for i in my_Artist_list], "testing whether Passion Pit's id in list")
	def test_Genres1(self):
		self.assertIn( "alternative dance", [i.genres[0] for i in my_Artist_list], "testing whether passion pit's first genre correct")		
	def test_Name2(self):
		self.assertIn('The Faceless', [i.artist_name for i in my_Artist_list], "testing whether the Faceless is in list")
	def test_Id2(self):
		self.assertIn("1FQ6uth7icR6Jhla16K2vC", [i.artist_id for i in my_Artist_list], "testing whether the Faceless' id is in the list")
	def test_Genres2(self):
		self.assertIn("brutal death metal", [i.genres[0] for i in my_Artist_list], "testing whether the Faceless's first genre is correct")

class GetRelatedArtist(unittest.TestCase):
	def test_length(self):
		self.assertEqual(len(the_faceless.get_related_artists(my_spotify_related)), 20, "testing whether length of GetRelatedArtist list correct")
	def test_name(self):
		self.assertIn("Job For A Cowboy", [ i.artist_name for i in the_faceless.get_related_artists(my_spotify_related)], "testing whether related artist name shows up")		
	def test_id(self):
		self.assertIn("5L3QTPofDwMPGlNnQkyHK1", [ i.artist_id for i in the_faceless.get_related_artists(my_spotify_related)], "testing whether related artist id shows up")		

unittest.main(verbosity=2)
