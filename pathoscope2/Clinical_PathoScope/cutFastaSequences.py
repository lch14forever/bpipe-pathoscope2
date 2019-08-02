#!/usr/bin/python
#cutFastaSequences.py
#Author: Allyson Byrd and Joseph Perez-Rogers
#Purpose:Trim reads in a fasta file to a specified length
#Input: Directory, name of input reads, desired length 
#Output: New fastq file with reads trimmed to desired length
#Usage: python cutFastaSequences.py /directory input.fastq 50

import os, sys

filename = sys.argv[1]
desiredLength = int(sys.argv[2])

directory = os.path.dirname(filename)
filename = os.path.basename(filename)

file = open('%s/%s' % (directory, filename), 'r')
fh = open('%s/%s_%s' % (directory, desiredLength, filename), 'w')

count = 0
for line in file:
	if count % 2 != 0:
		line = line.strip()
		if len(line) > desiredLength:
			line = line[0:desiredLength]
		fh.write("%s\n" % line)
	else:
		fh.write(line)
	count += 1
file.close()
fh.close()


