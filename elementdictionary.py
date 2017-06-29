



def Elements():
	ElementList = {}
	with open('elementdictionary.txt') as f:
		for index,line in enumerate(f):
			if len(line)>1:
				data = line.split()
				#print data[2].upper(), data[0]
				ElementList.update({data[2].upper():data[0]})

	return ElementList

