#this is a python file that grabs the frequency information from GAMESS output because I'm 
#too lazy to go in to the file manually. 
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
			#print modes
			#if "I" in modes:
			#	modes.remove("I")
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
	#the numbers are close and happy. Floating point and all that
	#bullshit. 
	Q = 0.0
	first = 0.0
	second = 0.0
	if len(v1) != len(v2):
		print "You don't have the same amount of frequecies in each file you silly billy."
		return False 
	else:
		#[float(2.9979248 * vib) for vib in v1]
		#[float(2.9979248 * vib) for vib in v2]
		
		#print v1[0], v2[0],T, lnb(v1[0],T),'sdfafd'
		for i in range(0,len(v1)):
			#print lnb(v1[i],T)
			#Q = Q + lnb(v1[i],T) - lnb(v2[i],T)
			first = first + lnb(v1[i],T)
			second = second + lnb(v2[i],T)
	#	print first, second
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
			#if v1[i]==v2[i]:
				#continue
			#else:
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
		#if v1[i]==v2[i]:
		#	continue
		#else:
			count +=1
			u_1 = hok/T*freqscale(v1[i])
			u_2 = hok/T*freqscale(v2[i])
			
			err1 = (u_1*err)**2#(err*freqscale(v1[i])*10**10)**2
			err2 = (u_2*err)**2#(err*freqscale(v2[i])*10**10)**2
		

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
			if i == j: #and v1[i]!=v2[i]:
				u_1 = hok/T*freqscale(v1[i])
				u_2 = hok/T*freqscale(v2[i])
				
				err1 = (u_1*err)
				err2 = (u_2*err)
				total_corr +=  errorslice(u_1) * errorslice(u_2)*err1*err2
	return -2*total_corr

v1 = [3828.49 ,
3825.3 ,
3824.39 ,
3812.55 ,
3811.62 ,
3752.13 ,
3744.14 ,
3739.33 ,
3730.08 ,
3728.25 ,
1658.71 ,
1649.82 ,
1639.98 ,
1639.93 ,
1638.25 ,
644.7 ,
615.42 ,
608.46 ,
583.25 ,
505.14,
422.3 ,
402.45 ,
390.28 ,
373.26 ,
367.09 ,
336.07 ,
285.32 ,
285.2 ,
284.42 ,
261.62 ,
248.83 ,
245.16 ,
238.22 ,
171.77 ,
168.61 ,
130.97,
127.62 ,
111.76 ,
72.19 ,
67.81 ,
51.5 ,
42.45 ]

v2= [3828.49
,3825.3
,3824.39
, 3812.55
, 3811.62
,3752.13
, 3744.14
, 3739.33
, 3730.08
, 3728.25
, 1658.71
, 1649.82
, 1639.98
, 1639.93
,1638.25
, 645.1
, 615.42
, 608.69
,583.27
, 505.4
, 424.17
, 403.04
, 390.28
, 373.26
, 368.11
, 336.08
, 285.33
, 285.29
, 284.72
,261.7
, 248.83
, 245.76
,238.22
, 172.36
,168.79
, 130.98
, 128.35
,111.88
, 72.25
, 67.86
,51.5
,42.45]

for i in range(len(v2)):
	v1[i] = float(v1[i])
	v2[i] = float(v2[i])
#Remember to use the LOG CORRELATION or else your're rinning into a weird precision issue that I didn't feel like fixing

#print(np.exp(rpf(v2,v1,300)),rpf2(v1,v2,300) ,uncertainty(v1,v2,300,.050),uncertainty2(v1,v2,300,0.05))
#print(CorCorrect(v1,v2,300,0.05)+uncertainty2(v1,v2,300,0.05)**2)#

#print(logCorCorrect(v1,v2,300,0.05)+uncertainty(v1,v2,300,0.05)**2)
#print(np.sqrt(logCorCorrect(v1,v2,300,0.05)+uncertainty(v1,v2,300,0.05)**2))

