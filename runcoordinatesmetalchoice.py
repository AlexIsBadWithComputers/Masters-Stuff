#Interface to use coordinate grab


from coordinategraballmetals import *
import sys
from elementdictionary import *

Choices = Elements()

MyElements = {}
ignore =1 

print ""
print "Hi diddle ho neighborino! Lets walk through what you want me to grab in terms of Cu stuff from the pdb file!"
print "First, what is the file name of the .pdb file you want me to take a lookie loo through?"
try:
	while True:

		try:
			file = raw_input("File Name: ")
			file = str(file)
			open(file, 'r')
			break
		except IOError:
			print "Oh my, the file", file," does not exist, please type more effectively"
	

		except:
			pass
	print ""
	print "What would you like your outputfiles to be named? (note they will all have *.inp, and have an extra number if multiple structures)"
	print ". Do not include file extensions"

	print ""
	while True:
		out = raw_input("File name: " )
		if "." in out:
			print "I said no file extensions! No! Try again."
			print ""
		else:
			out = str(out)
			break


	print""
	print " What metals are you looking for?"
	print""
	while True:
		try:
			atom = raw_input("Atom: " ).upper()
			atom = str(atom)
			MyElements.update({atom:Choices[atom]})
		except KeyError:
			print atom, " is not an element according to my dictionary, try again"
		
		while True:
			print"Do you want to look for more metals?"
			more = raw_input("Y/N " ).upper()
			if more == "N":
				done = True
				break
			if more =="Y":
				done = False
				break
			else:
				print "Please type only Y or N"
				print""
		if done == True:
			print" You will be looking for the following metals in, " ,file
			for keys in MyElements:
				print keys
			break	




	print""
	print "Do you want extra amino acids? Or just those directly bound to the your chosen metals?"
	while True:
		extra = str(raw_input("y/n? "))
		if extra.lower() == "y":
			change = raw_input("How many extra (on each side)? ").strip(".")
			change = int(change)
			break
		if extra.lower() == "n":
			change = 0
			break
		else:
			print ""
			print "That was not a 'y' or an 'n', try again"
			print ""
	print "Sometimes depending on the formatting of the LINK group in your pdb file, the order of amino acids might change in a way unexpected"
	print "by the function that adds extra amino acids. If the default setting returned molecules that weren't closely linked, you may benefit"
	print "from switching the parameter that controls this. Were your molecules peculiar? If so, would you like to switch the parameter?"
	print ""
	while True:
		switch = raw_input("Would you like to switch? (Y/N) ")
		if switch.lower()=="y":
			print "Switching index...."
			ignore = 2
			break
		if switch.lower() == 'n':
			print "Okay."
			break
		else:
			print "Please enter Y or N "
			print""

except KeyboardInterrupt:
		print ""
		print "Quitting so soon? That's okay, I didn't put a lot of effort into writing this or anything."
		sys.exit()

GrabbyPants(file,out,MyElements,change,ignore)
print ""
print "I am done, your files are in this directory."