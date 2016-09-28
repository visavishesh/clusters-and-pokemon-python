from lxml import html
import json
import pprint
import time
import requests
import requests_oauthlib
from requests_oauthlib import OAuth1
from sets import Set

poke_list=[]
f = open('pokemon.txt', 'r')
for line in f:
	poke_list+=[unicode(line.strip(), "utf-8")]
f.close()

entries={}

with open('pokemon-sightings.txt') as data_file:    
    if data_file!=None:
    	entries = json.load(data_file)

out_of_pages=False
page_number=1
while not(out_of_pages):
	url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=nycpokespawn&count=4000&page='+str(page_number)
	with open('config.txt') as config_file:    
    if config_file!=None:
    	config = json.load(config_file)
    	twitter_oauth_app_key=config["twitter_oauth_app_key"]
    	twitter_oauth_app_secret=config["twitter_oauth_app_secret"]

	auth = OAuth1(twitter_oauth_app_key, twitter_oauth_app_secret)
	headers = {'user-agent': 'my-python-application'}
	time.sleep(.01)
	page = requests.get(url, auth=auth)
	data = json.loads(page.content)
	if data==None or data==[]: 
		#print "Out of Pages"
		out_of_pages=True
	#print "New Page"
	for item in data:
		#print "Iteration"
		entry = {}
		line = item["text"]
		if len(line)>0:	
			#print "Data Entry"
			name=item["text"].partition("at")[0].strip()
			location = item["text"].partition("at")[2].partition("until")[0].strip()
			time_code = item["text"].partition("at")[2].partition("until")[2].partition("#PokemonGo")[0].strip()
			entry["date"] = item["created_at"]
			if len(item["entities"]["urls"])>0:
				geocodes = item["entities"]["urls"][0]["display_url"]				
				#google_page = requests.get("http://"+geocodes)
				#google_page_content = google_page.url
				entry["geo_url"] = geocodes
			else:
				entry["geo_url"] = None

			if name in poke_list:
				#if the pokemon is not in the dict
				if not entries.get(name):
					#make an item for that name
					entries[name]={}
					#add that location to that name
					entries[name][location]={}
					#add the entry to that time code under that location
					entries[name][location][time_code]=[entry["geo_url"]]
				#if the pokemon is in the dict
				else:
					if entries[name].get(location):
						if entries[name][location].get(time_code):
							if not(entry["geo_url"] in entries[name][location][time_code]):
								entries[name][location][time_code]+=[entry["geo_url"]]
						else:
							entries[name][location][time_code]=[entry["geo_url"]]
					else:
						entries[name][location]={}
						entries[name][location][time_code]=[entry["geo_url"]]
			else: 
				#print "error"
				#print page_number
				pass
		else:
			#print "Out of Pages"
			out_of_pages=True
			break
	if page_number>20: 
		#print "More than 20 pages"
		out_of_pages=True
		break
	else:
		page_number+=1

with open('pokemon-sightings.txt', 'w') as outfile:
     json.dump(entries, outfile, sort_keys = True, indent = 4,
ensure_ascii=False)
outfile.close()

for key in entries.keys():
	print str(key)+": "
	for location in entries[key]:
		print "\t"+str(location),": "
		for time in entries[key][location]:
			print "\t\t"+str(time)+": "+str(entries[key][location][time])


#page = requests.get('https://twitter.com/search?q=at%2C%20until%20from%3Anycpokespawn&src=typd', headers=headers, auth=auth)
#time.sleep(.04)
#tree = html.fromstring(page.content)
#block_link = '//p[@class="TweetTextSize  js-tweet-text tweet-text"]/a[not(@class="twitter-hashtag pretty-link js-nav")]'
#blocks = tree.xpath(block_link)
#data_link = '//p[@class="TweetTextSize  js-tweet-text tweet-text"]'
#data = tree.xpath(data_link)
#for i in range(len(blocks)):
#	print (data[i].text.strip(),blocks[i].attrib['title'].strip())