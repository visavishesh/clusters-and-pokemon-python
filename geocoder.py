import json 
import requests

geocodes={}
with open('geocodes.txt') as geocodes_file:    
    if geocodes_file!=None:
    	geocodes = json.load(geocodes_file)

with open('pokemon-sightings.txt') as data_file:    
    if data_file!=None:
    	entries = json.load(data_file)

geocoding_base_url = "https://maps.googleapis.com/maps/api/geocode/json?address="
with open('config.txt') as config_file:    
    if config_file!=None:
    	config = json.load(config_file)
    	api_key=config["google_maps_api_key"]

size=0 
for pokemon in entries:
	for location in entries[pokemon]:
		if geocodes.get(location):
			print "Found",geocodes[location]			
			pass
		else: 
			address_components = location.split()
			address = ""
			for component in address_components:
				address+=str(component)
				if address_components.index(component)!=len(address_components)-1:
					address+="+"
			geocoding_url = geocoding_base_url+address+"&key="+api_key
			google_page = requests.get(geocoding_url).content
			google_page = json.loads(google_page)
			lat_long = {}
			if google_page!=None and google_page!={} and len(google_page["results"])!=0:
				lat_long["lat"]=google_page["results"][0]["geometry"]["location"]["lat"]
				lat_long["long"]=google_page["results"][0]["geometry"]["location"]["lng"]
				if lat_long!=None and lat_long!={}:
					geocodes[location]=lat_long					
				print geocodes[location]
		if size%100==0:
			with open('geocodes.txt', 'w') as outfile:
			     json.dump(geocodes, outfile, sort_keys = True, indent = 4,
			ensure_ascii=True)
			outfile.close()
		size+=1

with open('geocodes.txt', 'w') as outfile:
     json.dump(geocodes, outfile, sort_keys = True, indent = 4,
ensure_ascii=True)
outfile.close()
print geocodes, size