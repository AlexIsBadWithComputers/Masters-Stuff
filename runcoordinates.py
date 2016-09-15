#Interface to use coordinate grab


from coordinategrabmod import *
import sys


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
	print "Do you want extra amino acids? Or just those directly bound to the Cu?"
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
except KeyboardInterrupt:
		print ""
		print "Quitting so soon? That's okay, I didn't put a lot of effort into writing this or anything."
		sys.exit()

grabbypants(file,out,change)
print ""
print "I am done, your files are in this directory."