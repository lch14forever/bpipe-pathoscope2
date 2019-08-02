#!/usr/bin/python
#splitSequences.py
#Authors: Allyson Byrd and Joseph Perez-Rogers
#Purpose: Checks the length of the sequences in the given fastq file and determines if read splitting is required
#Input: fasta file, desired length
#Output: True or False reads need to be split
#Usage: python checkLength.py 

def checkLength(inputFasta,desiredLength):

	lineCount = 0 
	read_lengths = []
	split = False
	ic = 0
	maxlen = 0

	infile = open(inputFasta, 'r')

	for line in infile:
		line = line.strip()
		ic += 1
		if ic == 2:
			if len(line) > desiredLength:
				split = True
				break
			elif len(line) > maxlen:
				maxlen = len(line)
		elif ic == 4:
			ic = 0
		
		lineCount += 1

	infile.close()

	if split:
		return True
	else:
		return False
