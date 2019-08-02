#!/usr/bin/python
#updatedfastq.py
#Author: Allyson Byrd and Joseph Perez-Rogers
#Purpose: Update a fastq file to reflect what aligned or didn't align in a sam file
#Inputs: Sam file, fastq file, 1 (keep aligned reads) or 0 (keep unaligned reads)
#Outputs: Updated fastq files with reads which did or did not align depending on sys.argv[3], text file of number of hits to each subject sequence
#Usage: python updatedfastq.py samFile input.fastq output.fastq output.txt 1 

import sys

#1 = keep aligned reads 0 = keep unaligned reads
keepWhat = int(sys.argv[1])

if keepWhat == 1:
	keepAligned = True
else:
	keepAligned = False

outFile = sys.argv[2]

#1 = host alignment, 0 = not host alignment
hostQ = int(sys.argv[3])
if hostQ == 1:
	o_fastq = sys.argv[4]
	nsys = 5
else:
	o_fastq = False
	nsys = 4

hitIndex = {}

f = open(outFile,'w')
unaligned = 0

#parsing the sam file to see which reads aligned and didn't align 
for i in range(nsys,len(sys.argv)):
	alignments = 0
	infile = open(sys.argv[i], 'r')
	
	#check if we need to read in the original fastq file for host alignment
	if o_fastq != False:
		o_fastq = open(o_fastq,'r')

	counter = 0
	for line in infile:
		#bypassing the reference headers 
		if line.startswith('@'):
			counter = 0
		else:
			#WITHIN SAM FILE
			counter += 1
			line = line.strip().split('\t')
			#name of read that aligned 
			read = line[0]
			#sum of thrown flags 
			value = int(line[1])
			#reference sequence the read aligned to  
			rname = line[2]
			#nucleotide sequence
			seq = line[9]
			#per-base quality scores
			quals = line[10]		

			#WITHIN FASTQ FILE
			if o_fastq != False:
				o_rname = o_fastq.readline()
				o_seq = o_fastq.readline()
				o_pl = o_fastq.readline()
				o_quals = o_fastq.readline()
			
			#keepWhat==1 retain aligned read
			#8 flag unset means alignment is the primary alignment
			if keepAligned == True:
				if value & 2**8 == 0 and value & 4 == 0:
					try:
						hitIndex[counter]
						pass
					except:
						hitIndex[counter] = True
						f.write("@"+read+"\n"+seq+"\n+"+read+"\n"+quals+"\n")
				else:
					#4 bit flag not set, read had an additional alignment
					pass
			
			#keepWhat==0 retain unaligned read
			elif keepAligned == False:
				#hostQ=0 this is not an alignment against the host database
				if hostQ != 1:
					if value & 4 == 0: #If 4 bit flag not set means read had alignment
						try:
							hitIndex[counter] #check if this read index is already in the dictionary
						except:
							hitIndex[counter] = True #adding this read index to the dictionary
					else:
						pass #4 bit flag not set, read had an additional alignment

				#hostQ=1 this is an alignment against the host database and since the reads were trimmed, we need to read in the untrimmed fastq file to recover the original reads 
				elif hostQ ==1:
					if value & 4 != 0:
						f.write(o_rname+o_seq+o_pl+o_quals)
					else:
						#4 bit flag not set, read had an additional alignment
						pass
	infile.close()
# Looping back through the last SAM file and writing a new fastq file containing only unique unaligned reads (this loop is only accessed when writing a fastq file of unaligned non-host alignment reads)
if keepWhat==0 and hostQ==0:
	infile = open(sys.argv[len(sys.argv)-1], 'r')
	counter = 0
	for line in infile:
		#bypassing the reference headers 
		if line.startswith('@'):
			counter = 0
		else:
			#WITHIN SAM FILE
			counter += 1
			line = line.strip().split('\t')
			#name of read that aligned 
			read = line[0]
			#sum of thrown flags 
			value = int(line[1])
			#reference sequence the read aligned to  
			rname = line[2]
			#nucleotide sequence
			seq = line[9]
			#per-base quality scores
			quals = line[10]		
			try:
				hitIndex[counter]
			except:
				f.write("@"+read+"\n"+seq+"\n+"+read+"\n"+quals+"\n")
	infile.close()
f.close()

				
