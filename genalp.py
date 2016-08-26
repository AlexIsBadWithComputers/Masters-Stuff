#this will generate values of Alpha for cases with N>=2 atoms

from itertools import permutations
import itertools
import os
import sys
from collections import defaultdict
from freqgrab import *



def listup(list): #Force capitals so your input file can be all topsy turvy. 
	return map(str.upper,list)
#finds the location of CU in the input file (so the numbers are right for the exchange)
def CuLocation(file):
   
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
        	if count - 2 < 0:
        		pass #sanitize input
        	else:
				subs.append(count-2) #-2 because first two lines are symetry and descritption.
 
        if "$END" in listup(line.split()):
            if BC == 0:
            	continue
            else:
                break
       
          
    return subs

#first, we must generate our set

def gen(N): #Input is number of atoms to exchange, assumes two isotopes
	light = ["L" for i in range(N)]
	out = []
	new = light
	out.append(light[:]) #PYthon being goofy
	for i in range(N):
		new[i] = "H"
		out.append(new[:])

	return out

def TotalPerms(replaced):
	units = []
	for col in replaced:
		units.append(list(set(permutations(col,len(col)))))

	return list(units)
#find multiplicative factors
def MultFact(logue): 
	count = 0 
	for iso in logue:
		if iso == "H":
			count+=1
	return count

#This creates a dictionary of all relevant data for the 
#calculation of fractionation factors involving
#multiple isotope exchanges
def DictBuilder(N): 
	ToRun = {}
	RequiredForms = TotalPerms(gen(N))
	for forms in RequiredForms:
		for form in forms:
			num = MultFact(form)
			denom = abs(num - len(form))
			ToRun.update({form:[num,denom]})
		

	return ToRun




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

#This builds the required input file to calculate vibrational modes. 
#It assumes the calculation is already complete, which is good. 
#Otherwise we'd have much waiting to do
def GAMESS(form,locations,file): #locations is Culocation(filename)
	os.chdir("/media/a10/878b7269-cf84-4703-b765-ccc01a18b528/home/a10/gamess")
	massarray = []
	allvibs = []
	for i, atoms in enumerate(form):
		if atoms == "H":
			massarray.append(''.join([" $mass amass(",str(locations[i]),")= 64.9277929", " $end \n"]))
		if atoms == "L":
			massarray.append(''.join([" $mass amass(",str(locations[i]),")= 62.9295989", " $end \n"]))

	header = GrabInput(file)
	hessian = GrabHessian(''.join([file.strip("inp"),"dat"]))
	print "grabbed it"

	temp = open("temp.inp",'w')
	temp.write(" $force rdhess=.t. $end \n")
	for lines in massarray:
		temp.write(lines)

	header = GrabInput(file)
	hessian = GrabHessian(''.join([file.strip("inp"),"dat"]))
	os.system("pwd")
	for lines in header:
		temp.write(lines)
	temp.write('\n')
	for lines in hessian:
		temp.write(lines)
	temp.write('\n')	
	temp.close()

	os.system(' '.join(["./rungms temp.inp 00 8 | tee temp.txt"]))
	os.system("rm temp.r*")
	#calculate our vibs
	size = len(othergrabber("temp.txt"))
	allvibs.append(othergrabber("temp.txt"))
	os.system("rm temp.d*")
	os.system("rm temp.txt")


	outvibs = [float(i) for i in allvibs[0]]
	return outvibs

	


os.chdir("/media/a10/878b7269-cf84-4703-b765-ccc01a18b528/home/a10/gamess")
file = "TriNuc6-spinmult4fixhess.inp"


systems = DictBuilder(3)

#Now we choose which form that everything is relative to (the lightest is the obvious choice)
relative = GAMESS(["L" for i in range(len(CuLocation(file)))],CuLocation(file),file)
temperatures = [100 + i for i in range(0,250,5)]
os.chdir("/home/a10/GradSchoolStuff/codes")

#os.mkdir(directory)
for molecules in systems:
	#print ''.join([molecules[0],molecules[1],molecules[2],".txt"])
	savfrac = []
	os.chdir("/media/a10/878b7269-cf84-4703-b765-ccc01a18b528/home/a10/gamess")
	vibs = GAMESS(molecules,CuLocation(file),file)
	for temp in temperatures:
		savfrac.append(1000 * rpf(relative,vibs,float(temp))) 
	os.chdir("/home/a10/GradSchoolStuff/codes/TriNuc6-spinmult4fixhess")
	outfile = open(''.join([molecules[0],molecules[1],molecules[2],"2",".txt"]),'w')
	for i in range(len(savfrac)):
		outfile.write('{} {} {}'.format(savfrac[i],temperatures[i],'\n'))
	outfile.close()
	










