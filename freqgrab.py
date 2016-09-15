#I use this file as something to dump things I think I might implement later.  
##filename = raw_input("Enter the file name which you want to grab frequency information from: ")
#filename = 'diditwork.txt'
#filename2 = 'vib63.txt'
import numpy as np
import math


def fil(val): #Ignore imaginary frequencies
	if "I" in val:
		return 0

def vibgrabber(filename): #searches GAMESS output to find vibrational spectra, including translational/rotational modes.
	with open(str(filename),"r") as f: 
		search = f.readlines()
		f.close

	vibs = []
	ReadBegin = False
	for i, line in enumerate(search):
		if "THERMOCHEMISTRY" in line:
			ReadBegin = False
		if ReadBegin == True:
			if len(line.split()) > 2:
				Info = line.split()
				vibs.append(float(Info[1]))
		if "MODE FREQ(CM**-1)  SYMMETRY  RED. MASS  IR INTENS." in line:
			ReadBegin = True 
		if "WARNING" in line:
			print search[i:i+3]
	return vibs
	
def linearsearch(array,k): #return k largest values. Obviously, heap search will be faster. But this data set will always pretty small. 
	return sorted(array,reverse=True)[:k]

def othergrabber(filename): #this one is in case the "Modes" section doesn't get printed off
	with open(str(filename),"r") as f: 
		search = f.readlines()
    	f.close

	vibs = []
	ReadBegin = False

	for i, line in enumerate(search):
		if "FREQUENCY:" in line:
			modes = line.split()
			
			for j in range(1,len(modes)):
				if "I" in modes[j]:
					modes[j].strip("I")
				else:
					vibs.append(float(modes[j]))
		if "WARNING" in line:
			print search[i:i+3]
	return vibs

def lnb(freq,T): #make life esier
	hok = .479924466 #h/k
	freq = freq * 2.9979248 
	if freq !=0: #Rotation or translation

		lnb = -np.log(freq) + 0.5 *hok* freq / T + np.log(1.0 - np.exp(-hok*freq / T))
	else: 
		lnb = 0.0
	return lnb

def rpf(v1,v2,T): #reduced partition function
	#remember to scale frequencies by 10^-10. Not a big deal. It's so
	#the numbers are close and happy.
	Q = 0.0
	first = 0.0
	second = 0.0
	if len(v1) != len(v2):
		print "You don't have the same amount of frequecies in each file you silly billy."
		return False 
	else:
	
		for i in range(0,len(v1)):
			first = first + lnb(v1[i],T)
			second = second + lnb(v2[i],T)
		Q = first - second
		
		return Q
def freqscale(freq): #scale frequencies
	return freq * 2.9979248


def rpf2(v1,v2,T):
	beta = 1
	hok = .479924466 #h/k

	if len(v1) != len(v2):
		print "You don't r i the same amount of frequecies in each file you silly billy."
		return False 
	else:
		for i in range(len(v1)):
			u1 = hok/T*freqscale(v1[i])
			u2 = hok/T*freqscale(v2[i])
			beta = beta* u1/u2*np.sinh(u2/2)/np.sinh(u1/2)
				
		return beta

 
def errorslice(val):
	return  (1/val - .5/np.tanh(val/2))
def uncertainty(v1,v2,T,err):
	#this propogates uncertainty assuming an error err in each vibrational mode. Note this is u(ln(beta))
	if len(v1) != len(v2):
		print "You don't have the same amount of frequecies in each file you silly billy."
		return False 
	hok = .479924466 #plank over boltz

	total_error = 0.0
	for i in range(0,len(v1)):
		u_1 = hok/T*freqscale(v1[i])
		u_2 = hok/T*freqscale(v2[i])

		err1 = (err*u_1)**2
		err2 = (err*u_2)**2

		total_error += (errorslice(u_1)**2)*err1 + (errorslice(u_2)**2)*err2

	total_error = np.sqrt(abs(total_error))
	return total_error

def uncertainty2(v1,v2,T,err):
	if len(v1) != len(v2):
		print "You don't have the same amount of frequecies in each file you silly billy."
		return False 
	hok = .479924466 #plank over boltz

	total_error = 0.0
	count = 0
	for i in range(0,len(v1)):
	
		count +=1
		u_1 = hok/T*freqscale(v1[i])
		u_2 = hok/T*freqscale(v2[i])
			
		err1 = (u_1*err)**2
		err2 = (u_2*err)**2
		
		total_error += rpf2([u_1],[u_2],T)**2 * (errorslice(u_1)**2 * err1 + errorslice(u_2)**2*err2)


	return np.sqrt(abs(total_error))

def CorCorrect(v1,v2,T,err):
	if len(v1) != len(v2):
		print "You don't have the same amount of frequecies in each file you silly billy."
		return False 
	hok = .479924466 #plank over boltz

	total_corr = 0
	for i in range(len(v1)):
		for j in range(len(v1)):
			if i == j: #and v1[i]!=v2[i]:
				u_1 = hok/T*freqscale(v1[i])
				u_2 = hok/T*freqscale(v2[i])
				
				err1 = (u_1*err)
				err2 = (u_2*err)
				total_corr += (u_1/u_2 * np.sinh(u_2/2)/np.sinh(u_1/2))**2 * errorslice(u_1) * errorslice(u_2)*err1*err2
	return -2*total_corr

def logCorCorrect(v1,v2,T,err):
	if len(v1) != len(v2):
		print "You don't have the same amount of frequecies in each file you silly billy."
		return False 
	hok = .479924466 #plank over boltz

	total_corr = 0
	for i in range(len(v1)):
		for j in range(len(v1)):
			if i == j: 
				u_1 = hok/T*freqscale(v1[i])
				u_2 = hok/T*freqscale(v2[i])
				
				err1 = (u_1*err)
				err2 = (u_2*err)
				total_corr +=  errorslice(u_1) * errorslice(u_2)*err1*err2
	return -2*total_corr


#Remember to use the LOG CORRELATION or else your're rinning into a weird precision issue that I didn't feel like fixing

#print(np.exp(rpf(v2,v1,300)),rpf2(v1,v2,300) ,uncertainty(v1,v2,300,.050),uncertainty2(v1,v2,300,0.05))
#print(CorCorrect(v1,v2,300,0.05)+uncertainty2(v1,v2,300,0.05)**2)#

#print(logCorCorrect(v1,v2,300,0.05)+uncertainty(v1,v2,300,0.05)**2)
#print(np.sqrt(logCorCorrect(v1,v2,300,0.05)+uncertainty(v1,v2,300,0.05)**2))

