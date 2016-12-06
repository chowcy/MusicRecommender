#Cathy Chow
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

#Can change this if you don't want to use my cache
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
		#list of names of artists liked on facebook
		self.list_artists = [artist['name'] for artist in fb_data['music']['data']]

	def __str__(self):
		return self.user_name

	#REQUIRES: dictionary of liked artists' data from Spotify
	#EFFECTS: returns list of Artist objects for each artist user like that has Spotify data
	def get_Artist_list(self, artist_data_dict):

		return [ Artist(artist_data_dict[artist]) for artist in artist_data_dict ]


	#REQUIRES: dictionary of  liked artists' data from Spotify
	#		   dictionary of the related artists of those artists (so it can be passed into the Artist constructor
	#EFFECTS:  returns list of all related artists for all users' liked artists, sorted from most frequent to least
	def top_related_artists(self, artist_data_dict, related_artist_data):
		freq_dict = {}
		Artist_list = self.get_Artist_list(artist_data_dict)
		for artist in Artist_list:
			#if manage to get related artists for that artist
			if artist.get_related_artists(related_artist_data) != None: 

				for related_artist in artist.get_related_artists(related_artist_data):

					#only include recommendations for artists that the user does not already like
					if related_artist.artist_name not in [artist.artist_name for artist in Artist_list]:
						if related_artist.artist_name in freq_dict:
							freq_dict[related_artist.artist_name] += 1
						else:
							freq_dict[related_artist.artist_name] = 1
		return [ freq[0] for freq in sorted(freq_dict.items(), key = lambda (x, y): y, reverse = True) ]

	#REQUIRES: dictionary of  liked artists' data from Spotify
	#EFFECTS:  returns list of all genres for all users' liked artists, sorted from most frequent to least
	def top_genres(self, artist_data_dict):
		freq_dict = {}
		Artist_list = self.get_Artist_list(artist_data_dict)
		for artist in Artist_list:
			if len(artist.genres) > 0: 
				for genre in artist.genres:
					if genre in freq_dict:
						freq_dict[genre] += 1
					else:
						freq_dict[genre] = 1
		return [ freq[0] for freq in sorted(freq_dict.items(), key = lambda (x, y): y, reverse = True) ]

class Artist():
	def __init__(self, artist_data):
		self.artist_name = artist_data['name'].encode('utf-8')
		self.genres = artist_data['genres']
		self.artist_id = artist_data['id']

	def __str__(self):
		return self.artist_name

	def get_related_artists(self, related_artist_data):
	#there may be artists that we could find searches for, but which have no related artists.
	#if no related artists were found, will go to except block
		try:
			related_artists = related_artist_data[self.artist_id]
			#if related artists exist, return related artists list
			return [ Artist(artist) for artist in related_artists ]
		except: 
			pass

def print_menu(menu_type, limit = 100):
	print '*************************************'
	if menu_type == 'start':
		print 'What would you like to do?'
		print 'A: Get top recommended artists.'
		print 'B: Get your top genres.'
		print 'Q: Quit this program.'
		print 
	elif menu_type == 'top related':
		print 'How many recommended artists would you like to output?'
		print 'Cannot exceed ' + str(limit) + ' artists.'
	elif menu_type == 'write to file':
		print 'Would you like to write this to a .txt file?'
		print 'If yes, type Y'
		print 'If no, type N'
	elif menu_type == 'youtube':
		print 'Would you like to listen to some of these artists on YouTube?'
		print 'This will open a tab on your web browser for each artist on YouTube, so you must have an internet connection.'
		print 'If no, type N'
		print 'If yes, type how many artists you would to listen to on YouTube'
		print 'Cannot exceed ' + str(limit) + ' artists.'
	elif menu_type == 'genres':
		print 'How many top genres would you like to output?'
		print 'Cannot exceed ' + str(limit) + ' genres.'

def interaction_driver(user, spotify_artist_info, spotify_related_info):
	print "Hello! Welcome to Cathy's Music Recommendation Program!"
	print_menu('start')
	user_input = raw_input()
	while user_input != 'Q':
		if user_input == 'A':

			#print top recommendations depending on how many they want
			top_recs = user.top_related_artists(spotify_artist_info, spotify_related_info)
			print_menu('top related', len(top_recs))
			num_recs = int(raw_input())
			for i in top_recs[:num_recs]:
				print i

			#ask if they'd like this information saved to a file
			print_menu('write to file')
			to_write = raw_input()
			if to_write == 'Y':
				file_name = raw_input('Please enter a file name without the .txt extension.')
				f = open(file_name + '.txt', 'w')
				for i in top_recs[:num_recs]:
					f.write(i)
					f.write('\n')
				f.close()

			#ask if they'd like to listen to this artist on YouTube
			#will open web browser depending on how many artists they want to listen to
			print_menu('youtube', len(top_recs))
			num_youtube = raw_input()
			try:
				#will fail if a non-number was inputted. Meaning No.
				num_youtube = int(num_youtube)
				for artist in top_recs[:num_youtube]:
					youtube_url = 'https://www.youtube.com/results?search_query=' + artist + '&page=&utm_source=opensearch'
					webbrowser.open(youtube_url)
			except:
				pass
			

		elif user_input == 'B':
			#print top genres depending on how many they want
			top_genres = user.top_genres(spotify_artist_info)
			print_menu('genres', len(top_genres))
			num_genres = int(raw_input())
			for i in top_genres[:num_genres]:
				print i

			#ask if they'd like this information saved to a file
			print_menu('write to file')
			to_write = raw_input()
			if to_write == 'Y':
				file_name = raw_input('Please enter a file name without the .txt extension.')
				f = open(file_name + '.txt', 'w')
				for i in top_genres[:num_genres]:
					f.write(i)
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
	fb_response = requests.get(fb_base_url, params= fb_params_dict)
	fb_data = fb_response.json()

	is_more = True
	#check if need to do paging
	try:
		next_url = fb_data['music']['paging']['next']
	except KeyError as e:
		#invalid oauth
		if e.message == 'music':
			print 'Invalid Oauth. Either expired or empty. Please get a fresh token from Facebook.'
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

#################################################################################################

print 'Creating FacebookUser instance'
user = FacebookUser(fb_data)

##############################GET SPOTIFY SEARCH AND CACHE#######################################
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
for artist_name in user.list_artists:
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

#######################GET SPOTIFY RELATED ARTISTS AND CACHE#########################################

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
for artist in user.get_Artist_list(spotify_artist_info):
	#artist name has been found and is in cache
	try: 
		if spotify_related_cache[artist.artist_id] != 'none':
			spotify_related_info[artist.artist_id] = spotify_related_cache[artist.artist_id]

	#related artists have not been searched for
	except KeyError as e:

		print 'Making related artists request to Spotify API'
		token_response = requests.post(base_url_token, data = param_token_dict, auth = (client_id, client_secret))
		token_dict = token_response.json()
		access_token = token_dict['access_token']
		header_dict_token = {'Authorization': ('Bearer ' + access_token)}
		param_search_dict['id'] = artist.artist_id
		related_response = requests.get((base_url_related + artist.artist_id + '/related-artists'), headers = header_dict_token)
		artist_related_data = related_response.json()	

		#if at least one artist is returned from related results
		if len(artist_related_data['artists']) > 0:
			spotify_related_info[artists.artist_id] = artist_related_data['artists']
			spotify_related_cache[artist.artist_id] = artist_related_data['artists']

		#no search results found :(
		else:
			print 'No related artists found for ' + artist.artist_name
			print 'Removing ' + artist.artist_name + ' from analysis'
			spotify_related_cache[artist.artist_id] = 'none'

f = open(spot_related_cache_fname, 'w')
f.write(json.dumps(spotify_related_cache))
f.close()
###################################################################################################################

interaction_driver(user, spotify_artist_info, spotify_related_info)

##UNIT TESTS USING MY FACEBOOK ACCOUNT
# me = FacebookUser(fb_data)
# test_artist = {
# 'name': 'sample name',
# 'id': 'sample id',
# 'genres': ['rock', 'pop', 'jazz']
# }
# class FacebookUserClass(unittest.TestCase):

# 	def test_name(self):
# 		self.assertEqual(me.user_name, 'Cat Chow', "testing facebook user's name") 
# 	def test_id(self):
# 		self.assertEqual(me.user_id, '10153037726223192', "testing facebook user's id #") 
# 	def test_list_artists1(self):
# 		self.assertEqual(me.list_artists[0], 'Passion Pit', "testing facebook user's first music like")
# 	def test_list_artists2(self):
# 		self.assertEqual(me.list_artists[-1], 'Cradle of Filth', "testing facebook user's last music like")

# class ArtistClass(unittest.TestCase):

# 	def test_name(self):
# 		self.assertEqual(Artist(test_artist).artist_name, 'sample name', "testing whether name correct")		
# 	def test_id(self):
# 		self.assertEqual(Artist(test_artist).artist_id, 'sample id', "testing whether id correct")
# 	def test_genres(self):
# 		self.assertEqual(Artist(test_artist).genres, ['rock', 'pop', 'jazz'], "testing whether genres correct")

# class ArtistList(unittest.TestCase):

# 	def test_first_id(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[0].artist_id, '7gjAu1qr5C2grXeQFFOGeh', "testing whether first artist id is correct")	
# 	def test_first_name(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[0].artist_name, 'Passion Pit', "testing whether first artist name is correct")
# 	def test_first_genre_f(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[0].genres[0], 'alternative dance', "testing whether first genre of first artist is correct")
# 	def test_first_genre_l(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[0].genres[-1], 'synthpop', "testing whether last genre of first artist is correct")

# 	def test_last_id(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[-1].artist_id, '0NTSMFFapnyZfvmCwzcYPd', "testing whether last artist id is correct")	
# 	def test_last_name(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[-1].artist_name, 'Cradle Of Filth', "testing whether last artist name is correct")
# 	def test_last_genre_f(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[-1].genres[0], 'alternative metal', "testing whether first genre of last artist is correct")
# 	def test_last_genre_l(self):
# 		self.assertEqual(me.create_Artist_obj_list(spotify_search_cache_dict)[-1].genres[-1], 'symphonic black metal', "testing whether last genre of last artist is correct")

# unittest.main(verbosity=2)

# 		print '_____________________________'
# 		print 'ARTIST RECOMMENDATIONS FOR: ' + artist_name
# 		#http://stackoverflow.com/questions/30557409/python-spotify-api-post-call
		#make request to get audio features about a song. requires token
	# 	r = requests.post(base_url, data = param_dict, auth = (client_id, client_secret))
	# 	python_dict = r.json()
	# 	access_token = python_dict['access_token']
	# 	#get audio features using token
	# 	header_dict_token = {'Authorization': ('Bearer ' + access_token)}
	# 	r = requests.get((base_url_token + artist_id + '/related-artists'), headers = header_dict_token)
	# 	related_artist_dict = r.json()

	# 	for item in related_artist_dict['artists']:
	# 		try:
	# 			print item['name']
	# 		except:
	# 			print 'No recommended artists for: ' + artist_name
	# except:
	# 	print 'No spotify artist called ' + artist_name


# def create_artist_obj_list(artist_id_list):
# 	print 'Making request to Spotify Get Several Artists endpoint'

# 	#Get Several Artists has a maximum of 50
# 	#Figure out how many requests need to be made
# 	MAX_ARTISTS = 50
# 	lst_length = len(artist_id_list)
# 	num_requests = lst_length / MAX_ARTISTS
# 	if lst_length % MAX_ARTISTS != 0:
# 		num_requests += 1

# 	artist_obj_list = []
# 	for i in range(num_requests):
# 		param_artists_dict = {}
# 		#ids value is ids separated by commas
# 		artist_id_list_50 = artist_id_list[(MAX_ARTISTS * i):]
# 		param_artists_dict['ids'] = ','.join(artist_id_list_50)

# 		artists_response = requests.get(base_url_artists, params = param_artists_dict)
# 		artists_data = artists_response.json()['artists']
# 		artist_obj_list += [Artist(artist) for artist in artists_data]
# 	return artist_obj_list