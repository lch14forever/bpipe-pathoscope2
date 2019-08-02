#!/usr/bin/python
#combineSams.py
#Author: Allyson Byrd and Joseph Perez-Rogers
#Purpose: Combines multiple sam files into a single sam file 
#Input: Name of the output file and sam files to combine
#Output: Combined sam file
#Usage: python combineSams.py /file_path/combined.sam /file_path/sam1 /file_path/sam2

import sys, os

outFile = sys.argv[1]
#samFiles are listed in the remainder of the command line arguments 

#headers written to one file and reads written to another
#2 files are concatenated at the end 
cSam_file = open("%s" % (outFile), 'w')

header_count = []
nsams = 0
#looping through each of the sam files 
for sam in sys.argv:
	if nsams < 2:
		pass
	else:
		SAM_FILE = open(sam, 'r')
		line = SAM_FILE.readline()
		count = 0
		while line.startswith('@'):
			count += 1
			cSam_file.write(line)
			line = SAM_FILE.readline()
		SAM_FILE.close()
		header_count.append(count)	
	nsams += 1 

cSam_file.close()

if nsams > 2:
	nsams = 0
	for i,sam in enumerate(sys.argv):
		if nsams < 2:
			pass
		else:
			cline = "tail -n +%i %s >> %s" %(header_count[i-2]+1,sam,outFile)
			os.system(cline)
		nsams += 1 

