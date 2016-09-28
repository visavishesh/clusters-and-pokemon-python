import json
import re
import math
import numpy as np
import random
import sys
import datetime

pokemon_list=[]
with open('pokemon.txt') as data_file:    
    if data_file!=None:
    	for line in data_file:
    		pokemon_list+=[line]
data_file.close()

class Point:
    def __init__(self,dims,weight=1.0):
        self.dims=dims
        self.num_dim=len(dims)
        self.weight=weight
        self.edges=[]

    def print_point(self):
    	out = ""
    	for i in range(self.num_dim): 
    		item = self.dims[i]
    		out+=str("%8f" % item)    		
    		if i != self.num_dim-1: 
    			out+=", "
    	out+=" "+str(len(self.edges))
    	return out

class Node:
    def __init__(self,data,weight=1.0):
        self.data=data
        self.weight=weight

    def print_node(self):
    	out = ""
    	for key in self.data:     		
    		out+=key+": "+str("%8f " % self.data[key])    		
    	return out

class Edge:
    def __init__(self,source,dest,weight):
        self.source=source
        self.dest=dest
        self.weight=weight

    def print_edge(self):
    	out = ""
    	for key in self.data:     		
    		out+=str("%8f " % self.data[key])
    	return out

def node_dist(p1,p2,keys,weights):	
	partial_sum=0.0
	for i in range(len(keys)):
		key = keys[i]
		a1 = p1.data[key]
		a2 = p2.data[key]
		if key in keys:
			partial_sum+=pow((a2-a1)*weights[i],2)
	if partial_sum!=0:
		return math.sqrt(partial_sum)
	else:
		return -1

def probabilityNodes(node_o,nodes_o,keys,weights):	
	prob = 0.0
	bounds={}
	nodes=nodes_o
	node=node_o
	for key in keys:
		val_list = [vertex.data[key] for vertex in nodes]
		min_bound = float(min(val_list))
		max_bound = float(max(val_list))
		bounded_range = max_bound-min_bound
		#print bounded_range
		if bounded_range==0: bounded_range=.0000001
		bounds["min_bound"]=min_bound
		bounds["max_bound"]=max_bound
		bounds["bounded_range"]=bounded_range		
		node.data[key] = float((node.data[key]-min_bound)/bounded_range)				
		for other in nodes:
			other.data[key] = float((other.data[key]-min_bound)/bounded_range)			
	for other in nodes:
		prob+=other.weight*(1-node_dist(node,other,keys,weights))
	prob/=len(nodes)*len(keys)
	return prob

def genTestNode(nodes):
	return Node({"lat":40.741085,"lng":-73.979240,"time":now_seconds},1.0)

def seconds_to_hms(time_code):
	out=""
	h=int(time_code/3600)
	time_code-=3600*h
	m=int(time_code/60)
	time_code-=60*m
	s=int(time_code)
	out+= str(h)+":"+str(m)+":"+str(s)+" "
	return out

def h_m_s_to_seconds(time_code):
	time_array = time_code.split(":")
	now_seconds = 60*60*int(time_array[0])+60*int(time_array[1])+float(time_array[2])
	return now_seconds

def point_dist(p1,p2):
	dim_lists=[]
	partial_sum=0.0
	for dim in range(p1.num_dim):
		a1 = p1.dims[dim]
		a2 = p2.dims[dim]
		partial_sum+=pow((a2-a1),2)			
	return math.sqrt(partial_sum)

def area(points):
	if len(points)==3:
		a=point_dist(points[0],points[1])
		b=point_dist(points[0],points[2])
		c=point_dist(points[1],points[2])
		s = (a+b+c)/2
		return math.sqrt(s*(s-a)*(s-b)*(s-c))

	if len(points)==4:
		return area([points[0],points[1],points[2]]) + area([points[0],points[2],points[3]])
	return False

def pointInRect(point, rect):
	p=point
	a=rect[0]
	b=rect[1]
	c=rect[2]
	d=rect[3]
	APD=[a,p,d]
	DPC=[d,p,c]
	CPB=[c,p,b]
	PBA=[p,b,a]
	rect_area=area(rect)
	if ((area(APD)+area(DPC)+area(CPB)+area(PBA)-area(rect))<.0000001): 
		return True
	if (area(APD)+area(DPC)+area(CPB)+area(PBA))*1000000>rect_area*1000000: 
		return False
	else:	
		return True

def genCorners(center=(40.729040, -73.992630),factor=.4,rotate=5,slim=.5):	

	ref=("up", "left")
	out_of_bounds=(45.729040, -90.992630)

	NW_x=center[0]+factor*slim
	NW_y=center[1]-factor
	NW_x2=(NW_x - center[0])*math.cos(rotate) - (NW_y - center[1])*math.sin(rotate)+center[0]
	NW_y2=(NW_x - center[0])*math.sin(rotate) + (NW_y - center[1])*math.cos(rotate)+center[1]
	
	NE_x=center[0]+factor*slim	
	NE_y=center[1]+factor
	NE_x2=(NE_x - center[0])*math.cos(rotate) - (NE_y - center[1])*math.sin(rotate)+center[0]	
	NE_y2=(NE_x - center[0])*math.sin(rotate) + (NE_y - center[1])*math.cos(rotate)+center[1]

	SW_x=center[0]-factor*slim
	SW_y=center[1]-factor
	SW_x2=(SW_x - center[0])*math.cos(rotate) - (SW_y - center[1])*math.sin(rotate)+center[0]	
	SW_y2=(SW_x - center[0])*math.sin(rotate) + (SW_y - center[1])*math.cos(rotate)+center[1]

	SE_x=center[0]-factor*slim
	SE_y=center[1]+factor
	SE_x2=(SE_x - center[0])*math.cos(rotate) - (SE_y - center[1])*math.sin(rotate)+center[0]	
	SE_y2=(SE_x - center[0])*math.sin(rotate) + (SE_y - center[1])*math.cos(rotate)+center[1]

	return [Point([NW_x2,NW_y2]),Point([NE_x2,NE_y2]),Point([SE_x2,SE_y2]),Point([SW_x2,SW_y2])]

def buildMatrix(dimensions, intensities=False):	
	matrix = []	
	for i in range(len(dimensions[0]["list"])):
		dim_list=[]
		for j in range(len(dimensions)):			
			min_bound = float(dimensions[j]["bounds"][0])
			max_bound = float(dimensions[j]["bounds"][1])
			bounded_range = (max_bound*1000000-min_bound*1000000)/1000000
			if bounded_range==0: bounded_range=.0000001
			val = float((dimensions[j]["list"][i]-min_bound)/bounded_range)
			dim_list+=[val]		
		point = Point(dim_list)
		if intensities: 
			point.weight=1.0
		matrix+=[point]
	return matrix

def getDataBounds(dim_grid):
	bound_list={}
	for dim in dim_grid:
		dim_list = dim_grid[dim]
		bounds = (float(min(dim_list)), float(max(dim_list)))
		bound_list["dim"]=bounds
	return bound_list

def buildDataMatrix(data_list, intensities=False):
	dim_grid={}
	bound_list=[]
	for dim in data_list[0]:
			dim_grid[dim]=[]

	for data_point in data_list:
		dim_array = []
		for dim in data_point:
			dim_array+=[data_point[dim]]			
			if data_point!=[] and data_point!=None:
				dim_grid[dim]+=[data_point[dim]]
		coordinate = Point(dim_array)	

	dimensions = [{"list":lat_list,"bounds":lat_bounds},{"list":lng_list,"bounds":lng_bounds},{"list":time_list,"bounds":time_bounds}]

	matrix = []	
	for i in range(len(dimensions[0]["list"])):
		dim_list=[]
		for j in range(len(dimensions)):			
			min_bound = float(dimensions[j]["bounds"][0])
			max_bound = float(dimensions[j]["bounds"][1])
			bounded_range = (max_bound*1000000-min_bound*1000000)/1000000
			if bounded_range==0: bounded_range=.0000001
			val = float((dimensions[j]["list"][i]-min_bound)/bounded_range)
			dim_list+=[val]		
		point = Point(dim_list)
		if intensities: 
			point.weight=1.0
		matrix+=[point]
	return matrix

def mergePoints(point1,point2,limit=1):
	if not(point1): return point2
	if not(point2): return point1	
	if point_dist(point1,point2)<=limit:
		point3=Point([],1.0)
		for var in range(len(point1.dims)):
			weights=point1.weight+point2.weight
			point3.dims+=[(point1.dims[var]*point1.weight+point2.dims[var]*point2.weight)/(weights)]
		point3.weight=point1.weight+point2.weight
		return point3
	else:
		return False

def matrixMerge(matrix,point1,point2,point3):	
	if point_dist(point1,point2)<20:
		if point1: matrix.remove(point1)
		if point2: matrix.remove(point2)
		if point3: matrix+=[point3]
	return matrix

def brute_merge_pass(matrix, sensitivity):
	new_matrix=[]
	for i in xrange(0,len(matrix)-1,1):	
		merging_result = mergePoints(matrix[i],matrix[i+1],sensitivity)
		if merging_result: new_matrix += [merging_result]
	return new_matrix

def calc_matrix_stats(matrix):
	if matrix==None or matrix==[] or len(matrix)<=1 or matrix==False: 
		return None
	matrix_stats={"stats":[],"length":0}
	for i in range(len(matrix[0].dims)-1):
		stat={}
		column = [point.dims[i] for point in matrix]
		stat["average"] = np.average(column)
		stat["coeff_var"] = np.std(column)/stat["average"]
		matrix_stats["stats"]+=[stat]
	matrix_stats["length"]=len(matrix)
	return matrix_stats

def run_brute_cluster(matrix):
	zoom=7
	stats=calc_matrix_stats(matrix)
	orig_size = len(matrix)
	coeff_var = np.average([item[1] for item in stats[:len(stats)-1]])
	while(len(matrix)>math.sqrt(orig_size)*2*coeff_var):
		stats=calc_matrix_stats(matrix)
		sensitivity=np.average([item[1] for item in stats[:len(stats)-1]])*zoom
		matrix=brute_merge_pass(matrix, 1/sensitivity)
		zoom+=1	
	return matrix

def find_closest_pair(matrix, pair=[], min_dist=sys.maxint):
	if len(matrix)==0: return False
	if len(matrix)==1: return False
	if len(matrix)==2: return matrix
	else:
		left = find_closest_pair(matrix[len(matrix)/2:], pair, min_dist)
		right = find_closest_pair(matrix[:len(matrix)/2], pair, min_dist)
		if left==False or left==None:
			if right==False: return False
			else: return right
		else:
			if right==False or right==None: return left
			else:
				a=left[0]
				b=left[1]
				c=right[0]
				d=right[1]
				distances=[min_dist,point_dist(a,b),point_dist(a,c),point_dist(a,d),point_dist(b,c),point_dist(b,d),point_dist(c,d)]
				pairs=[pair,[a,b],[a,c],[a,d],[b,c],[b,d],[c,d]]
				min_dist = min(distances)
				pair = pairs[distances.index(min_dist)]
				return pair
	return False

def run_closest_pairs_cluster(matrix):
	#matrix = sorted(matrix, key=lambda k: (k.dims[0],k.dims[1],k.dims[2]) )	
	points=find_closest_pair(matrix)
	if points==False: return matrix
	coeff_var=False
	if points:
		matrix = matrixMerge(matrix,points[0],points[1],mergePoints(points[0],points[1]))				
		stats=calc_matrix_stats(matrix)
		if stats!=None: 
			coeff_var = np.average([dim["coeff_var"] for dim in stats["stats"]])			
	if len(matrix)>20*coeff_var: 
		return run_closest_pairs_cluster(matrix)
	else: return matrix

def findClusters(dimensions):
	data = []	
	num_dim = len(dimensions)
	transform_bounds = []
	for dim in dimensions:
		min_bound = float(dim["bounds"][0])
		max_bound = float(dim["bounds"][1])
		bounded_range = max_bound-min_bound
		transform ={}
		transform["min_bound"]=min_bound
		transform["max_bound"]=max_bound
		transform["bounded_range"]=bounded_range
		transform_bounds+=[transform]
	clusters=[]
	intensities=True
	matrix = buildMatrix(dimensions, intensities)	
	if matrix==None or matrix==[] or len(matrix)==0 or matrix==[Point([0.0, 0.0, 0.0], 1.0)]: return []
	matrix=run_closest_pairs_cluster(matrix)
	for item in matrix:	
		new_row=[]
		for i in range(num_dim):
			dim = transform_bounds[i]
			lower=dim["min_bound"]
			upper=dim["max_bound"]
			bounded_range=dim["bounded_range"]
			new_row+=[item.dims[i]*bounded_range+lower]
		point = Point(new_row,item.weight)
		clusters+=[point]
	return clusters

def findClustersJSON(dimensions, keys):
	data = []	
	num_dim = len(dimensions)
	transform_bounds = []
	for dim in dimensions:
		min_bound = float(dim["bounds"][0])
		max_bound = float(dim["bounds"][1])
		bounded_range = max_bound-min_bound
		transform ={}
		transform["min_bound"]=min_bound
		transform["max_bound"]=max_bound
		transform["bounded_range"]=bounded_range
		transform_bounds+=[transform]
	clusters=[]
	intensities=True
	matrix = buildMatrix(dimensions, intensities)	
	if matrix==None or matrix==[] or len(matrix)==0 or matrix==[Point([0.0, 0.0, 0.0], 1.0)]: return []
	matrix=run_closest_pairs_cluster(matrix)
	for item in matrix:	
		new_row=[]
		point ={}
		for i in range(num_dim):
			dim = transform_bounds[i]
			lower=dim["min_bound"]
			upper=dim["max_bound"]
			bounded_range=dim["bounded_range"]
			new_row+=[item.dims[i]*bounded_range+lower]
			point[keys[i]]=item.dims[i]*bounded_range+lower
		clusters+=[point]
	return clusters

def genHotspots(coords):
	key_list= ["lat","lng","time"]
	pokemon_data = {}
	pokemon_data["geo"]={}
	pokemon_data["time"]={}
	pokemon_data["geo"]["hotspots"]=[]
	boundaries = genCorners()
	lat_list=[]
	lng_list=[]
	time_list=[]
	coords = sorted(coords, key=lambda k: k['time']*random.random()) 

	for data_point in coords:
		lat = data_point["lat"]
		lng = data_point["lng"]
		time = data_point["time"]
		coordinate = Point([lat, lng, time])
		if data_point!=[] and data_point!=None:
			lat_list+=[data_point["lat"]]
			lng_list+=[data_point["lng"]]
			time_list+=[data_point["time"]]			
			pokemon_data["geo"]["hotspots"]+=[coordinate]
	
	if lat_list==[] or lng_list==[] or time_list==[]:
		return pokemon_data
		
	lat_bounds = (float(min(lat_list)), float(max(lat_list)))
	lng_bounds = (float(min(lng_list)), float(max(lng_list)))
	time_bounds = (float(min(time_list)), float(max(time_list)))

	pokemon_data["geo"]["lat_bounds"]=lat_bounds
	pokemon_data["geo"]["lng_bounds"]=lng_bounds
	pokemon_data["time"]["time_bounds"]=time_bounds
	
	pokemon_data["geo"]["hotspots"] = findClustersJSON([{"bounds":lat_bounds,"list":lat_list}, {"bounds":lng_bounds,"list":lng_list}, {"bounds":time_bounds,"list":time_list}],key_list)
	return pokemon_data

def print_pokemon_data(hotspots, pokemon_list):
	key_list= ["lat","lng","time"]
	for pokemon in sorted(hotspots.keys(), key=lambda k:pokedexIndex(k,hotlist)): 	
	 	print "<------------------------------"+str(pokemon)+"----------------------------------->"
		for category in hotspots[pokemon].keys():		
			if category=="coords":
				print "\nCoordinates for Uploading to Map"			
				for item in hotspots[pokemon]["coords"]:
					print str(item["lat"])+", "+str(item["lng"])
				print "\nCoordinates"
				for item in hotspots[pokemon]["coords"]:
					print str(item["lat"])+", "+str(item["lng"])+", "+seconds_to_hms(item["time"])
				print "\n"
			elif category=="geo":
				print "Center: ",hotspots[pokemon]["geo"]["center"]						
				print "Hotspots: "
				for hotspot in hotspots[pokemon]["geo"]["hotspots"]:					
					out=""
					for index in range(len(hotspot)):
						if index==2: 
							time_code = float(hotspot[key_list[index]])
							out+= seconds_to_hms(time_code)
						else: out+=str(hotspot[key_list[index]])+" "
					print out
				print "\nHotspots For Map Uploading"
				for hotspot in hotspots[pokemon]["geo"]["hotspots"]:
					print str(hotspot[key_list[0]])+", "+str(hotspot[key_list[1]])					
				print "\n"
			else: 
				if category=="time":
					out=""
					time_code = hotspots[pokemon]["time"]["center"][0]					
					out+= seconds_to_hms(time_code)
					print "Center: ", out
					for item in hotspots[pokemon]["time"]["hours"][24]:
						if int(item)>12: 
							meridian="PM"
						else: meridian="AM"
						print int(item)%25, meridian, hotspots[pokemon]["time"]["hours"][24][item]
					print "\n"
					for item in hotspots[pokemon]["time"]["hours"][4]:						
						hour_range=( (int(item)*4)%25 , ((int(item)+1)*4)%25 )
						print hour_range, hotspots[pokemon]["time"]["hours"][4][item]
				else: print category,": ", hotspots[pokemon][category],"\n"	

def pokedexIndex(pokemon, hotlist):
	if pokemon in hotlist:
		return hotlist.index(pokemon)
	else:
		return 0

def generatePokemonData(hotlist=pokemon_list,time_filter=False, sorted_field="time"):
	hotspots = {}
	pokemon_entries =[pokemon for pokemon in entries.keys() if pokemon in hotlist]
	for pokemon in pokemon_entries:
		data_object = {}
		data_object["geo"]={}
		data_object["time"]={}
		data_object["geo"]["center"]=(0.0,0.0,0)
		data_object["geo"]["hotspots"]={}
		data_object["coords"]=[]
		data_object["time"]={}
		data_object["time"]["hours"]={}
		data_object["time"]["hours"][24]={}
		data_object["time"]["hours"][4]={}
		data_object["time"]["AM"]=0
		data_object["time"]["PM"]=0
		data_object["time"]["distribution"]=[(0.0,0.0)]
		data_object["time"]["center"]=(0.0,0)
		for location in [location for location in entries[pokemon] if geocodes.get(location)]:
			lat=geocodes[location]["lat"]
			lng=geocodes[location]["long"]			
			point = Point([lat,lng],1.0)
			if geocodes.get(location) and pointInRect(point,genCorners()):
				for time in entries[pokemon][location]:					
					h_m_s = time[:len(time)-4].split(":")
					day_night = time[len(time)-3:len(time)-1]
					if (re.search('[A-Za-z]', h_m_s[0])==None) and (re.search('[A-Za-z]', h_m_s[1])==None) and (re.search('[A-Za-z]', h_m_s[2])==None): 
						time_point=0.0
						h=int(h_m_s[0])
						if day_night=="PM": h+=12
						m=int(h_m_s[1])
						s=int(h_m_s[2])
						seconds = s+m*60+60*60*h
						if time_filter:			
							if abs(seconds-time_filter[0])>time_filter[1]: 
								continue
						if day_night=="AM" or day_night=="PM":
							if geocodes.get(location):								
								if data_object["time"]["hours"][24].get(h):
									data_object["time"]["hours"][24][h]+=1
								else:
									data_object["time"]["hours"][24][h]=1								
								if data_object["time"]["hours"][4].get(int(h%6)):
									data_object["time"]["hours"][4][int(h%6)]+=1
								else:
									data_object["time"]["hours"][4][int(h%6)]=1
								if data_object["time"].get(day_night):
									data_object["time"][day_night]+=1
								else:
									data_object["time"][day_night]=1

								lat_avg = float(data_object["geo"]["center"][0])
								lng_avg = float(data_object["geo"]["center"][1])
								geo_n = int(data_object["geo"]["center"][2])
								
								geo_new_n = geo_n+1
								lat_new_avg = ( (lat_avg * geo_n) + float(geocodes[location]["lat"]) )  / (geo_new_n)
								lng_new_avg = ( (lng_avg * geo_n) + float(geocodes[location]["long"]) ) / (geo_new_n)							
								data_object["geo"]["center"] = (lat_new_avg,lng_new_avg,geo_new_n) 

								time_avg = data_object["time"]["center"][0]
								time_n=data_object["time"]["center"][1]
								data_object["time"]["center"] = (int((time_avg*time_n+seconds)/(time_n+1)),time_n+1)

								coordinate = [{"lat":float(geocodes[location]["lat"]),"lng":float(geocodes[location]["long"]),"time":int(seconds)}]
								data_object["coords"] += coordinate
			hotspots[pokemon] = data_object							
		pokemon_data=genHotspots(hotspots[pokemon]["coords"])
		hotspots[pokemon]["geo"]["hotspots"]=pokemon_data["geo"]["hotspots"]
		hotspots[pokemon]["coords"] = sorted(hotspots[pokemon]["coords"],key=lambda k:k[sorted_field])
	return hotspots
	#end genHotspots()	


#begin main code <----------------------
entries={}

with open('pokemon-sightings.txt') as data_file:    
    if data_file!=None:
    	entries = json.load(data_file)
data_file.close()

geocodes={}
with open('geocodes.txt') as geocodes_file:    
    if geocodes_file!=None:
    	geocodes = json.load(geocodes_file)
geocodes_file.close()

hotlist=['Gengar','Muk','Machamp','Snorlax', 'Gyarados','Kabutops','Omastar','Dragonite', 'Lapras']
#now_seconds = h_m_s_to_seconds(str(datetime.datetime.now().time()))
#pokemon_data = generatePokemonData(hotlist, (now_seconds, 14400), sorted_field="time")
#print_pokemon_data(pokemon_data, pokemon_list)

with open('poke_loc.csv','w') as csv_file:    
    csv_file.write("uuid,lat,long,time\n")
    if csv_file!=None:
		pokemon_entries =[pokemon for pokemon in entries.keys() if pokemon in hotlist]
		for pokemon in pokemon_entries:
			for location in entries[pokemon]:
				for time in entries[pokemon][location]:
					for link in entries[pokemon][location][time]:
						h_m_s = time[:len(time)-4].split(":")+[time[len(time)-3:len(time)-1]]
						lat = geocodes[location]['lat']
						lng = geocodes[location]['long']
						if lat>39 and lat<41 and lng>-74 and lng<-73:
							h = int(h_m_s[0])
							m = int(h_m_s[1])
							s = int(h_m_s[2])
							mer = h_m_s[3]
							if mer=="PM":
								h=(h+12)%24
							time_code = str(h)+":"+str(m)+":"+str(s)
							seconds = h_m_s_to_seconds(time_code)
							times = {"h":int(h/1),"h2":int(h/12),"h4":int(h/6),"h6":int(h/4),"h12":int(h/2)}
							print pokemon,"| ",lat,lng," | ",time_code,mer," | ",seconds," | ",link, times
							csv_file.write(pokemon+","+str((lat-40)*800000)+","+str((lng+74.3)*400000)+","+str(seconds/240)+"\n")


"""for pokemon in [pmon for pmon in pokemon_data if pmon in hotlist]:
	print pokemon
	edges = []
	nodes = []
	key_list= ["lat","lng","time"]
	key_weights=[1.0,1.0,0.00001]
	for category in pokemon_data[pokemon]:	
		if category=="coords":			
			for coord in pokemon_data[pokemon][category]:
				vertex = Node(coord)
				nodes+=[vertex]	
				for other in pokemon_data[pokemon][category]:					
					if vertex!=other:
						dest_node = Node(other)
						weights = {}
						weight=node_dist(vertex,dest_node,key_list,key_weights)
						edge = Edge(vertex,dest_node,weight)
						edges+=[edge]						
	edges = sorted(edges,key=lambda k:k.weight)
	for i in range(10):
		test_node=genTestNode(nodes)
		training_node=Node({"lat":40.741085,"lng":-73.979240,"time":now_seconds},1.0)
		for item in pokemon_data[pokemon]["geo"]["hotspots"]:
			data={}
			for dim in item:				
				data[dim]=item[dim]			
			item_node = Node(data,1.0)
			#print 1/node_dist(item_node,training_node,key_list,key_weights)
		#prob_test = probabilityNodes(test_node,nodes,key_list,key_weights)
		#print prob_test"""

#with open('./pokemon-go-map/hotspot_data.json', 'w') as outfile:
#    json.dump(pokemon_data, outfile)
#outfile.close()
	

