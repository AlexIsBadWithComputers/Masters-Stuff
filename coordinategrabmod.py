#This is a python file to zip through the .pdb files to grab the data that I'd like to use
#could I have used something they offer on the site? Yes. Did I start this before I realised
#someone else had put everything together to work nicely for me? Yes. Do I regret it now?
#definitely. 
import struct
import networkx
from networkx.algorithms.components.connected import connected_components
import re

#Use this to sort which compunds are connected to eachother in the link group
def to_graph(l):
    G = networkx.Graph()
    for part in l:
        # each sublist is a bunch of nodes
        G.add_nodes_from(part)
        # it also imlies a number of edges:
        G.add_edges_from(to_edges(part))
    return G
def to_edges(l):
    """ 
        treat `l` as a Graph and returns it's edges 
        to_edges(['a','b','c','d']) -> [(a,b), (b,c),(c,d)]
    """
    it = iter(l)
    last = next(it)

    for current in it:
        yield last, current
        last = current    
#If you want more amino acids!
def extrabits(molecule, skip,pmr = 0):
	out = molecule[:]
	if pmr == 0:
		return molecule
	else:
		print pmr
		pm = []
		for i in range(-pmr,pmr):
			if i == 0:
				continue
			else:
				pm.append(i)


		for strings in molecule:
			if strings not in skip:
				#takind sturcture label, stripping it and adding pm to each side
				for num in pm:
					extra = int(re.sub("\D","",strings)) + num
					first = re.sub('\d+','',strings)
					add = "".join([first,str(extra)])
					#print add
					out.append(str(add))
		print out
		return out




def grabbypants(file,out,doubledown=0):

	#These are the format of the link and atom/hetatom sections respectively.
#This is important because we want to parse the data in a way that will
#give us the result we desire. For the love of god don't accidentally 
#delete those, typing that was honestly the hardest part. 

	linkform = "6s6x4s1s3s1x5s1s15s4s1s3s1x5s1s2x6s1x6s1x5s" 
	atomform = "6s5s1x4s1s3s1x5s1s3x8s8s8s6s6s10x2s2s1x"

#xyz positions in atom groups
	Xloc = 7  
	Yloc = 8
	Zloc = 9

	linkloc1 = 4 #column location of group identifier in link group
	linkloc2 = 10 #column location of group identifier in link group
	atomloc = 5 #column location of group identifier in atom/hetatom groups
	nameloc = 12 #location of atom name

#Fire up the data file
	with open(file,"r") as f:
		search = f.readlines()
 		f.close

	hangon = []
	coords = []
	matches = []
	culoc = []
	for i, line in enumerate(search):
		#no one cares about extra data until they forget which paper stuff came from
		#but I'm not writing it in because I'm a rule breaker
		if "REMARK" in line:
			continue
		if "HEADER" in line:
			continue
		if "ANISOU" in line:
			continue
		if "CONECT" in line:
			continue
		if "MASTER" in line:
			continue

		#link only applies to metals and junk, only care about copper so we're just doing that.
		if 'LINK' in line:
			if 'CU' in line:
				templine = struct.unpack(linkform,line.strip())
				hangon.append(templine)
				#need for later use with extrabits
				culoc.append(templine[linkloc1])
				print templine
				
		if "ATOM" in line and len(line.strip()) > 50:
			templine = struct.unpack(atomform,line)
			coords.append(templine)
		if "HETATM" in line and len(line.strip()) > 50:	 
			templine = struct.unpack(atomform,line)
			coords.append(templine)
		if "ENDMDL" in line:
			break 
			#Eventuall incorporate averages, but for my purpose 
			#variations in the models aren't important

	#Find out what is linked to what
	for i in range(0,len(hangon)):
		matches.append([hangon[i][linkloc2],hangon[i][linkloc1]])
	#Sort it for no real reason
	matches.sort()
	#Use the graph theory stuff to find out what's connected to what and extract that data
	G = to_graph(matches)
	comps = connected_components(G)

#MDesignate a place for each of the connections
	compounds = []
	for comp in comps:
		compounds.append(list(comp))

	#add any bonus amino acids if we need them 
	for i, molecule in enumerate(compounds):

		compounds[i] = list(extrabits(molecule,culoc[i],doubledown))

	molecules = [[] for i in range(0,len(compounds))]

	#Start connecting my lists and place each "molecule" in it's own index of the molecules array
	for k in range(0,len(compounds)):
		print compounds[k]
		for i in range(0,len(compounds[k])):
			for j in range(0,len(coords)):
				if compounds[k][i] in coords[j]:
					molecules[k].append([coords[j][nameloc],coords[j][Xloc],coords[j][Yloc],coords[j][Zloc],coords[j][atomloc]])
			
				

	#Write the molecule of interest to an input file
	for j in range(len(molecules)):
		file = open("".join([out, str(j), ".inp"]), "w")

		file.write(" $DATA")
		file.write('\n')
		file.write("Title")
		file.write('\n')
		file.write("C1")
		file.write('\n')
		for i in range(0,len(molecules[j])):
			molecules[j][i] = [x.strip(' ') for x in molecules[j][i]]
		charge = []
		#I got lazy here. If it  gets bigger I'll put everything in a dictionary. 
		for rows in molecules[j]:
			if "CU" in rows:
				charge.append("29.0")
				continue
			if 'C' in rows:
				charge.append("6.0")
				continue
			if 'N' in rows:
				charge.append("7.0")
				continue
			if 'O' in rows:
				charge.append("8.0")
				continue
			if 'S' in rows:
				charge.append("16.0")
				continue
			if 'H' in rows:
				charge.append("1.0")
			else:
				print "???", rows

		




		for i in range(0,len(molecules[j])):
			rows = molecules[0][i]
			file.write('{}     {}     {}     {}     {}'.format(rows[0],charge[i],rows[1],rows[2],rows[3]))
			file.write('\n')
		file.write(" $END")
		file.write('\n')
		file.close()


file = "/home/a10/GradSchoolStuff/molecules/ATOX1hah1/1fee.pdb"

#grabbypants(file,"thing",1)