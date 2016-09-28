

pf = open("pokego-data.txt", "r")
items = []
item = []

lines = pf.readlines()

for line_number in range(len(lines)):
	line = lines[line_number]
	if line.find("Items {\n")!=-1: 
		item = {}
	else:
		template_index = line.find("TemplateId: ")
		if template_index!=-1:
			key = "TemplateId"
			if line.find("sequence_"):
				data = line[template_index+22:len(line)-2]
				item["category"]="Sequence"
			else:
				data = line[template_index+13:len(line)-2]
			item[key]=data
			#print line
		else:
			colon_index = line.find(": ")
			bracket_index = line.find("{")
			if bracket_index!=-1:
				#print item["TemplateId"]
				line_number+=1
				attr_name = str(line[2:bracket_index-1])
				item["data"]={}
				close_index = line.find("}")
				data_item={}
				while close_index==-1:
					line=lines[line_number]
					close_index = line.find("}")
					line_number+=1
					if close_index==-1:
						input_string = line[15:len(line)-2].split()
						if len(input_string)>0: 
							if data_item.get(input_string[0])==None:
								data_item[input_string[0]]=input_string[1:]
							else:
								data_item[input_string[0]]+=input_string[1:]
						#print "-->",line[15:len(line)-2]
				item["data"][attr_name]=data_item
	items+=[item]

for item in items:
	print item
	if item["category"]!="Sequence":
		print ""
		for key in item.keys():
				print ""
				print key,": ", item[key]
