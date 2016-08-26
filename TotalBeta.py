#This sucker is to switch all choices that it finds in terms of Cu isotope substitution.

from itertools import permutations  
import os
import sys, getopt
from freqgrab import *

import itertools
def listup(list): #Force capitals so your input file can be all topsy turvy. 
	return map(str.upper,list)

def CuLocation(file):
    os.chdir("/home/a10/gamess")
    subs = []
    with open(file,'r') as f:
        input_card = f.readlines()
    f.close()
    BC=0
    count = 0
    for line in input_card:
    	count += 1
        if "$DATA" in listup(line.split()):
            BC = 1
            count = 0
            continue
        if "CU" in listup(line.split()) and BC==1:
            subs.append(count-2) #-2 because first two lines are symetry and descritption.
 
        if "$END" in listup(line.split()):
            if BC == 0:
            	continue
            else:
                break
       
          
    return subs





def myfilter(seq): 
   # order preserving
   noDupes = []
   [noDupes.append(i) for i in seq if not noDupes.count(i)]
   return noDupes
#Please note this problem grows quickly and after 7 isotope substitutions it takes about 40 seconds to find all possibilities
#I'm not worrying about it because the most I'll htopit is 3, but if anyone else ever uses this for large compounds, be
#aware that you may have to rewrite this. That said, 7 would have 448x2 diagonalizations of the Hessian, so this 40 seconds
#isn't really that big of a deal when you'll be waiting afew hours for that hahahahahahha 

#Just kidding, fixed it. Now the bottle neck is at 9 substitutions! Don't do that though, because it is too big. 
#It's almost like permutations scale like N! or something like that. (They do)

def IsotopicForms(Cu): #Find all isotopic forms of a molecule of a given Cu atom and prints out substitute or the static mass.
	if len(Cu) == 1:
		return [["Substitute"]]
	else:
		Choices = ["Substitute"]
		for i in range(len(Cu)-1):    #Fill list of correct size for the stuff
			Choices.append("Cu-65")
		for i in range(len(Cu)-1,2*(len(Cu)-1)):
			Choices.append("Cu-63")
		
			actual = []
		#If substitude isn't there, don't need that selection, also remove duplicate entries. 
		for perms in set(permutations(Choices,len(Cu))):
			if "Substitute" not in perms: 
				pass
			else:
				actual.append(list(perms))
		#if len(actual[0]) == 1:
		#	actual = [actual]
		#print actual, len(actual), "SDFSDFSDFSDF"
		return actual 
	
#hey = IsotopicForms(b)

def MassMaker(isotopologue):
	invariant = []
	changing = []
	for masses in isotopologue:
		for i in range(len(masses)):
			if len(masses[0]) == 2:
				changing.append(''.join([" $mass amass(",str(masses[1]),")=",str(masses[0][i]), " $end \n"]))
			if len(masses[0])!=2:
				invariant.append(''.join([" $mass amass(",str(masses[1]),")=",str(masses[0]), " $end \n"]))
	
	return invariant, changing

#This is a function that reads the array from IsotopicForms and prepares a loop to run each thorugh GAMESS
#Locations comes from Cu Locations

def GrabHessian(file):
	with open(file,'r') as f:
		findhess = f.readlines()
	f.close()
	stop = False
	TheHessian = []
	for lines in findhess:
		if "$HESS" in lines and stop ==False:
			stop = True 
		if stop == True:
			TheHessian.append(lines)
		if "$END" in lines and stop == True:
			break
	return TheHessian

def GrabInput(file):
	with open(file,'r') as f:
		data=f.readlines()
	f.close()
	stop = False
	InputData = []
	for lines in data:
		if "$DATA" in lines:
			stop = True
		if stop == True:
			if "$END" in lines:
				InputData.append(lines)
				break
		if "$guess" in lines: #ignore $vec read
			pass
		elif "$mass" in lines: #if you tried earlier I hate you
			pass
		else:
			InputData.append(lines)
	return InputData

def RunForms(forms,locations,file):
	FormDict = {"Cu-63": "62.9295989", "Cu-65":"64.9277929", 
	"Substitute" :  ["62.9295989", "64.9277929"]}
	temperatures = [100 + i for i in range(0,250,5)]
	os.chdir("/home/a10/gamess")
	
	allbeta = []
	for isotopologue in forms:
		savfrac = []
		InputList = []
		
		allvibs = []
		for i,atoms in enumerate(isotopologue):
			InputList.append([FormDict[atoms],locations[i]])
		#print InputList
		#print isotopologue
		invariant, changing = MassMaker(InputList)
		
		#Now we begin creating and running a whole whack of input files.
		header = GrabInput(file)
		hessian = GrabHessian(''.join([file.strip("inp"),"dat"]))
		for subs in changing:
			temp = open("temp.inp",'w')
			temp.write(" $force rdhess=.t. $end \n")
			temp.write(subs)
			for others in invariant:
				temp.write(others)
			for lines in header:
				temp.write(lines)
			temp.write('\n')
			for lines in hessian:
				temp.write(lines)

			temp.close()
			os.system(' '.join(["./rungms temp.inp 00 8 | tee temp.txt"]))
			os.system("rm temp.r*")
			#calculate our vibs
			size = len(othergrabber("temp.txt"))
			allvibs.append(linearsearch(othergrabber("temp.txt"),size))
			os.system("rm temp.d*")
			os.system("rm temp.txt")
		[float(i) for i in allvibs[0]]
		[float(i) for i in allvibs[1]]

		for temp in temperatures:
			savfrac.append(1000 * rpf(allvibs[0],allvibs[1],float(temp))) 
		allbeta.append(savfrac)
		
		
	return allbeta, temperatures
		






#Now that we've written all that, we'll actually get this little thing to produce some (formatted) output!

#print "Enter your *.inp file as well as the name of the main output."
inputfile = ''
#outputfile = ''
argv = sys.argv[1:]
try: 
	opts, args = getopt.getopt(argv,"hi::",["ifile="])
except getopt.GetoptError:
	print "You need to type TotalBeta.py -i <inputfile>"
	sys.exit()
for opt,arg in opts:
	if opt == '-h':
		print "TotalBeta.py -i <inputfile> "
	elif opt in ("-i", "--ifile"):
		inputfile = str(arg)
	

print list(IsotopicForms(CuLocation(inputfile)))
BetaValues,Temperatures = RunForms(IsotopicForms(CuLocation(inputfile)),CuLocation(inputfile), inputfile)

os.chdir("../GradSchoolStuff/codes")

print "" 
print "==================================="
print ""
print "   Results of Cu Isotope Analysis"
print ""
print "==================================="
print ""

if len(BetaValues) == 1:
	print "Only two Possible Cu Isotopologues in ", inputfile
	print ""
	outputfile = open(str(''.join([inputfile.strip(".inp"),"BetaValues.txt"])),'w')
	
	for i in range(len(BetaValues[0])):
		outputfile.write('{} {} {}'.format(BetaValues[0][i],Temperatures[i],'\n'))
	outputfile.close()
	
	print "Beta/Temperature information is in ", outputfile

elif len(BetaValues) != 1: 
	
	print "There are ", 2*len(BetaValues), "possible Cu isotopologues in ", str(inputfile)
	print ""
	
	outputfile = open(str(''.join([inputfile.strip(".inp"), "BetaValues.txt"])),'w')
	
	for i in range(len(BetaValues)):
		for j in range(len(BetaValues[i])):
			outputfile.write('{} {} {}'.format(BetaValues[i][j],Temperatures[j],'\n'))
		outputfile.write("\n")
		outputfile.write("\n")
	
	totalout = open(str(''.join([inputfile.strip(".inp"), "BetaValuesAverage.txt"])),'w')
	averagebeta = [float(sum(l)/len(l)) for l in zip(*BetaValues)] #Average of all beta
	
	for i,beta in enumerate(averagebeta):
		totalout.write('{} {} {}'.format(beta,Temperatures[i],'\n'))
	
	outputfile.close()
	totalout.close()

	print "All betas formatted for GNUplot are in ", str(outputfile), "and an average is avaiable in ", str(totalout), "."






