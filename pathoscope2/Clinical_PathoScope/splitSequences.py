#!/usr/bin/python
#splitSequences.py
#Authors: Allyson Byrd and Joseph Perez-Rogers
#Purpose: Splits reads in a fastq file into smaller segments of a desired length 
#Input: fasta file, desired length, minimum length 
#Output: fasta file where reads have been trimmed to a desired length 
#Usage: python splitSequences.py 

import sys, os

inputFasta = sys.argv[1]
outputFasta = sys.argv[2]
desiredLength = int(sys.argv[3])
minLength = int(sys.argv[4])

maxlen = 0
ic = 0
read_count = 0

infile = open(inputFasta, 'r')

print "\nSome reads in the fastq are longer than %s bp. These reads will be split into shorter segments of the desired length.\n" %(desiredLength)
outfile = open(outputFasta, 'w')
print "Now splitting reads...\n"
for line in infile:
	line = line.strip()
	ic += 1
	if ic == 1:
		rn = line
	elif ic == 2:
		seq = line
	elif ic == 3:
		p = line
	elif ic == 4:
		ic = 0
		qual = line
		if len(seq) <= desiredLength:
			outfile.write(rn+"\n"+seq+"\n"+p+"\n"+qual+"\n")
			read_count += 1
		else:
			si = 0
			while len(seq) > minLength:
				si += 1
				t_rn = "%s_segment%i" %(rn,si)
				t_p = "%s_segment%i" %(p,si)
				outfile.write(t_rn+"\n"+seq[0:desiredLength]+"\n"+t_p+"\n"+qual[0:desiredLength]+"\n")
				read_count += 1
				seq = seq[desiredLength:]
				qual = qual[desiredLength:]

outfile.close()
infile.close()
print "The new fastq file of shorter sequences has %i reads.\n" %read_count
