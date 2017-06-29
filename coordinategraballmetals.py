'''
This is a python file to zip through the .pdb files to grab the data that I'd like to use
could I have used something they offer on the site? Yes. Did I start this before I realised
someone else had put everything together to work nicely for me? Yes. Do I regret it now?
definitely. 
'''
import struct
import networkx
from networkx.algorithms.components.connected import connected_components
import re
from elementdictionary import *

AllElements = Elements()

'''
Use this to sort which compunds are connected to eachother in the link group
'''
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
'''
Adds extra amino acids to a molecule, while skipping the compounds 'next' to the metal
in the PDB file, and bonus is how many extra amino acids
'''
def extrabits(molecule, skip,bonus):
	out = molecule[:]
	pm = [-bonus,bonus]
	for strings in molecule:
		if strings in skip:
			continue
		elif strings not in skip:
			#takind sturcture label, stripping it and adding pm to each side
			for num in range(pm[0],pm[1]):
				extra = int(re.sub("\D","",strings)) + num
				first = re.sub('\d+','',strings)
				add = "".join([first,str(extra)])
				#print add
				out.append(str(add))
	print out
	return out

'''Takes in a .pdb file and writes a number of files starting with the header out.
Also takes in a dictionary of metals to search for along with their atomic number.
bonus is how many extra (if any) amino acids you desire, and ignore is 
a flag contolling which groups to ignore when grabbing extra amino acids from
the pdb file.
'''
def GrabbyPants(file,out,metals,bonus,ignore):

#This are the format of the link and atom/hetatom sections respectively.
#This is important because we want to parse the data in a way that will
#give us the result we desire. For the love of god don't accidentally 
#delete those, typing that was honestly the hardest part.


	linkform = "6s6x4s1s3s1x5s1s15s4s1s3s1x5s1s2x6s1x6s1x5s" 
	atomform = "6s5s1x4s1s3s1x5s1s3x8s8s8s6s6s10x2s2s1x"
	Find = list(metals.keys())
	FoundandIgnore = []
	#xyz positions in atom groups
	Xloc = 7  
	Yloc = 8
	Zloc = 9

	linkloc1 = 4 #column location of group identifier in link group
	linkloc2 = 10 #column location of group identifier in link group
	atomloc = 5 #column location of group identifier in atom/hetatom groups
	nameloc = 12 #location of atom name
	if ignore ==1:
		toignore = linkloc1
	if ignore == 2:
		toignore = linkloc2
	#Fire up the data files
	with open(file,"r") as f:
		search = f.readlines()
 		f.close

	hangon = []
	coords = []
	matches = []
	Wanted = ['ATOM','HETATM','LINK','ENDMDL']
	for i, line in enumerate(search):
	
		'''
		Ignoring a lot of information in the PDB file with this, 
		I recommend you look at it yourself to make sure you're 
		okay with my choice to ignore everything but coordinates.
		and the link group.
		'''
		if any(word in line for word in Wanted):

			#LINK tells you what groups are attached together if not in order.
			if 'LINK' in line: 
				
				if any(atom in line for atom in Find):
					
					#Don't want to add stuff in order which are attached 
					#to metals.
				
					FoundandIgnore.append(templine[toignore])
					templine = struct.unpack(linkform,line.strip())
					hangon.append(templine)
			#grab all the coordinates
			#ignor anisototropic contributions if any. 
			#you might be interested in these, but I am not
			if "ANISOU" in line and len(line.strip())>50:
				continue
					
			if "ATOM" in line and len(line.strip()) > 50:
				templine = struct.unpack(atomform,line)
				coords.append(templine)
			
			if "HETATM" in line and len(line.strip()) > 50:	 
				templine = struct.unpack(atomform,line)
				coords.append(templine)

			if "ENDMDL" in line:
				break #Eventuall incorporate averages

#Find out what is linked to what
	for i in range(0,len(hangon)):
		matches.append([hangon[i][linkloc2],hangon[i][linkloc1]])


	#Use the graph theory stuff to find out what's connected to what and extract that data
	G = to_graph(matches)
	comps = connected_components(G)

	#Designate a place for each of the connections
	compounds = []
	for comp in comps:
		compounds.append(list(comp))

	#Need to do everything again after adding new amino acids!
	if bonus > 0:
		
		newmatch = []
		for i in range(len(compounds)):
			junk = extrabits(compounds[i], FoundandIgnore,bonus)
			newmatch.append(junk)
		G = to_graph(newmatch)
		comps = connected_components(G)
		compounds = []
		for comp in comps:
			compounds.append(list(comp))
	
	molecules = [[] for i in range(0,len(compounds))]

	#Start connecting my lists and place each "molecule" in it's own index of the molecules array
	for k in range(0,len(compounds)):
		print compounds[k]
		for i in range(0,len(compounds[k])):
			for j in range(0,len(coords)):
				if compounds[k][i] in coords[j]:
					molecules[k].append([coords[j][nameloc],coords[j][Xloc],coords[j][Yloc],coords[j][Zloc],coords[j][atomloc]])
			
				

	'''
	Write the molecule of interest to an input file for GAMESS (with missing control parameters)
	'''
	
	for j in range(len(molecules)):
		f = open(str(out)+str(j)+".inp",'w')
		f.write("! PDB group labels used in this file \n ")
		printsequence =  ", ".join(compounds[j])
		f.write(" ".join(["!",printsequence]))
		f.write('\n')
		f.write(" $DATA")
		f.write('\n')
		f.write(str(file))
		f.write('\n')
		f.write("C1")
		f.write('\n')
		for i in range(0,len(molecules[j])):
			molecules[j][i] = [x.strip(' ') for x in molecules[j][i]]
		charge = []
		for rows in molecules[j]:
			if any(atom in AllElements for atom in rows):
				charge.append(AllElements[rows[0]])





		for i in range(0,len(molecules[j])):
			rows = molecules[j][i]
		#	print rows
			f.write('{}     {}     {}     {}     {}'.format(rows[0],charge[i],rows[1],rows[2],rows[3]))
			f.write('\n')
		f.write(" $END")
		f.write('\n')
		f.close()

#GrabbyPants('SOD/2c9v.pdb','stuff', {'CU':'29.0'},2,1)