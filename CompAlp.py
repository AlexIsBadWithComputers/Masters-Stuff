#Calculates a general alpha of big molecules
from itertools import permutations
import itertools
import os
import sys
from collections import defaultdict
import math

def counter(strings):
	out = []
	for things in strings:
		count = 0
		for letters in things:
			if "H" in letters:
				count += 1
		out.append(count)
	new = []
	nold = 69 #heh
	counted = []
	for items in out:
		n = out.count(items)
		if n == nold and items in counted:
			pass
		else:
			counted.append(items)
			new.append([items for i in range(n)])
			nold = n
	return new
def root(form):
	count = 0
	for letters in form:
		if letters == "H":
			count += 1
	return float(count)

def betamaker(files,*temp):
	#temp argument is if you just want one temperature
	#I probably do, but I though "What if I want more later
	#for an easy graph in the thesis?"
	#so I added it so i can be like "Thanks brobeans"
	#instead of the usual "Past Alex, you lazy piece of shit."
	
	associate = {}
	if temp:
		#print temp[0]
		for i, lines in enumerate(files):
			file = open("".join([files[i],".txt"]),'r')
			for lines in file:
				if " ".join(["",str(temp[0])]) in lines:
					#print lines.split()[0], files[i]
					total = float(lines.split()[0])
					new = math.exp(total/1000)
					associate.update({files[i].strip("2"):float(new)**(1/root(files[i]))})
					#print root(files[i]), files[i]
					#associate.update({files[i]:float(new)})
					#associate.update({files[i]:float(new)**(1./3.)})

	else:
		
		for i, lines in enumerate(files):
			out = []
			file = open("".join([files[i],".txt"]),'r')
			for lines in file:
				out.append(lines.split()[0])
			associate.update({files[i]:out})
		
	return associate
		
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

def alp(betas,B,R,N,temp):
	#beta is a N x M array where N is the 
	#permuations of isotopologues and 	
	#M is each temperature to calculate it as

	#R is the ratio of the thing it interacts with
	# and is oly valid if the other thing only
	#binds one atom of interest. Otherwise, 
	#good luck calculating this you poor bastard.

	#N is the number of atoms bound to the other 
	#molecule relevant to the exchange
	num = 0
	denom = 0
	#forms = gen(N)
	large = "".join(["H" for i in range(N)])

	
	Numbers = betamaker(files,temp)
	for key in Numbers:
		print Numbers[key],key
	
	for n in range(N):
		#N-n because it's easier to write the loop
		fact = (N-n) * R**((N-n-1))/(B**(N-n))
		for forms in TotalPerms(gen(N))[N-n]: #find which isotopologues we awnt
			entry = "".join(forms)
			num+= fact*Numbers[entry]**(N-n)
			print entry,N-n, "num",N-n-1
	
	
	for n in range(N):
		p = N-n-1
		fact2 = p* R**(n+1) / B**(n+1)
		for forms in TotalPerms(gen(N))[n+1]:
			if "".join(forms) == large:
				denom += N
				print forms, "hello",denom
			else:
				entry = "".join(forms)
				denom += fact2*Numbers[entry]**(n+1)
				print entry, p, "denom", n+1
	print num, denom, num/denom
		
	return num/denom
				
			




files = ["LLH2","LHL2","HLL2","LHH2","HLH2","HHL2","HHH2"]
files.reverse()

beta = math.exp(3.14994514474 /1000)
thing = math.exp((7.18406592455 /1000))
print (alp(files,beta,0,3,310)-1)*1000, "ANSWER", (1.0049237984/(beta)-1)*1000, thing, (beta/thing-1)*1000




