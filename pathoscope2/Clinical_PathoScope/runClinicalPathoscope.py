#!/usr/bin/python
#run_clinical_pathoscope.py
#Authors: Allyson Byrd and Joseph Perez-Rogers
#Purpose: Parses config file and generates Clinical Pathoscope pipeline shell script 
#Input: config file
#Output: shell script 
#Usage: python run_clinical_pathoscope.py config

import sys
import os
import checkLength

if len(sys.argv) > 1:
	config = sys.argv[1]
else:
	print "Error: No config file"
	print "Usage: python run_clinical_pathoscope.py config"
	sys.exit(1)
	
fastq_file = ''
target_dbs = []
host_filtration_dbs = []
filtration_dbs = []
#Clinical Pathoscope directory 
cp_dir = ''
db_dir = ''
bowtie2_bin = ''
searching_16S = False 
bowtie2_k = 10
bowtie2_quality = '--phred33' 
num_threads = 8
output_dir = ''
#Keep intermediate files 
keep_int = False 
#additional bowtie2 parameters 
parameter = '--very-sensitive'
usingPreloaded = False
max_read_length = 100

#Parsing the inputs in the config file
FILE_IN = open(config, 'r')
#fatal errors prevent the creation of the shell script 
fatal_errors = 0
for line in FILE_IN:
	if line.startswith('#'):
		pass
	if '=' in line:
		line = line.split('=')
		variable = line[0].strip()
		value = line[1].strip()
		
		#extensive error checking of all the user entered variables 
		if variable == '*filename':
			if os.path.exists(value):
				fastq_file = value
			elif not os.path.exists(value) and value != '':
				print 'Fatal Warning:%s does not exist' % value
				fatal_errors += 1
			else:
				pass
		elif variable == 'Preloaded_databases_directory':
			if value == '':
				pass
			elif os.path.exists(value):
				db_dir = value
			else:
				print 'Fatal Warning: The location of the databases %s does not exist' % value
				fatal_errors += 1
		elif variable == '*Target_Databases':
			canidates = value.split(',')
			for db in canidates:
				db = db.strip()
				if db.lower() == 'human':
					target_dbs.append('%s/hg19_rRNA' % db_dir)
					usingPreloaded = True
					#should we prevent the user from trying to make human the target?
				elif db.lower() == 'bacteria':
					target_dbs.append('%s/A-Lbacteria.fa' % db_dir)
					target_dbs.append('%s/M-Zbacteria.fa' % db_dir)
					usingPreloaded = True
				elif db.lower() == 'virus':
					target_dbs.append('%s/virus' % db_dir)
					usingPreloaded = True
				elif db != '':
					
					target_dbs.append(db)

		elif variable == 'Host_Filtration_Database':
			canidates = value.split(',')
			for db in canidates:
				db = db.strip()
				if db.lower() == 'human':
					host_filtration_dbs.append('%s/hg19_rRNA' % db_dir)
					usingPreloaded = True
				elif db.lower() == 'bacteria' or db.lower() == 'virus':
					print 'Warning: %s is not a valid HOST database' % db
					print "\tPlease list in 'Other_Filtration_Databases'"
				elif value != '':
					host_filtration_dbs.append(value)
								
		elif variable == 'Other_Filtration_Databases':
			canidates = value.split(',')
			for db in canidates:
				db = db.strip()
				if db.lower() == 'human':
					human_dir = '%s/human' % db_dir
					usingPreloaded = True
					if not human_dir in host_filtration_dbs:
						host_filtration_dbs.append('%s/human' % db_dir)
				elif db.lower() == 'bacteria':
					filtration_dbs.append('%s/A-Lbacteria.fa' % db_dir)
					filtration_dbs.append('%s/M-Zbacteria.fa' % db_dir)
					usingPreloaded = True
				elif db.lower() == 'virus':
					filtration_dbs.append('%s/virus' % db_dir)
					usingPreloaded = True
				elif db != '':
					filtration_dbs.append(db)
		
		elif variable == '*Clinical_Pathoscope_directory':
			if value == '':
				pass
			elif os.path.exists(value):
				cp_dir = value
			else:
				print 'Fatal Warning: The location of Clinical Pathoscope %s does not exist' % value
				fatal_errors += 1

		elif variable == '*bowtie2_bin':
			if value == '':
				pass
			elif os.path.exists(value):
				bowtie2_bin = value
			else:
				print 'Fatal Warning: The bowtie2 bin directory %s does not exist' % value
				fatal_errors += 1
				
		elif variable == '16S':
			if value == '':
				print "No value for '16S' was provided"
				print "\tBy default the pipeline will NOT be run for 16S sequences"
			elif value.lower() == 'no':
				#default variable for bowtie2_k and parameter remain
				pass  
			elif value.lower() == 'yes':
				bowtie2_k = 1000
				parameter = '--score-min L,-0.6,-0.07'
			else:
				print "Warning: '16S' must equal yes or no, not %s" % value
				print "\tBy default the pipeline will NOT be run for 16S sequences"
				
		elif variable == 'bowtie2_k':
			if value == '':
				print "No value for 'bowtie2_k' was provided"
				print "\tBy default the pipeline will be run with k = % s" % bowtie2_k
			else:
				try:
					value = int(value)
					if value < 0:
						print "Warning: 'bowtie2_k' must be greater than zero, not %s" % value 
						print "\tBy default the pipeline will be run with k = % s" % bowtie2_k
					else: 
						bowtie2_k = value
				except:
					print "Warning: 'bowtie2_k' must equal an integer, not %s" % value 
					print "\tBy default the pipeline will be run with k = % s" % bowtie2_k
		
		elif variable == 'bowtie_2_quality_score':
			if value == '':
				print "No value for 'bowtie_2_quality_score' was provided"
				print "\tBy default the %s option will be used" % bowtie2_quality
			elif value == '--phred33' or value == '--phred64' or value == '--solexa-quals' or value == '--int-quals':
				bowtie2_quality = value 
			else:
				print "Warning: %s is an invalid argument for 'bowtie_2_quality_score'" % value
				print "Valid arguments include: --phred33, --phred64, --solexa-quals, or --int-quals"
				print "\tBy default the %s option will be used" % bowtie2_quality
					
		elif variable == 'num_threads':
			if value == '':
				print "No value for 'num_threads' was provided"
				print "\tBy default the pipeline will be run with % s" % num_threads
			else:
				try:
					value = int(value)
					if value < 0:
						print "Warning: 'num_threads' must be greater than zero, not %s" % value 
						print "\tBy default the pipeline will be run with num_threads = % s" % num_threads
					else:
						num_threads = value
				except:
					print "Warning: 'num_threads' must equal an integer, not %s" % value 
					print "\tBy default the pipeline will be run with num_threads = % s" % num_threads
						
		elif variable == 'output_directory':
			if value == '':
				cwd = os.getcwd()
				print "Warning: No valid output directory given"
				print "\tBy default results will be written to %s" % cwd
				output_dir = cwd
			elif os.path.exists(value):
				output_dir = value 
			else:
				cwd = os.getcwd()
				print 'Warning: The output bin directory %s does not exist' % value
				print "\tBy default results will be written to %s" % cwd
				output_dir = cwd
				
				
		elif variable == 'keep_intermediate_files':
			if value == '':
				print "By default the intermediate files will be deleted"
			elif value.lower() == 'no':
				keep_int = False 
			elif value.lower()== 'yes':
				keep_int = True 
			else:
				print "Warning: 'keep_intermediate_files' must equal yes or no, not %s" % value
				print "\tBy default the intermediate files will be deleted"

FILE_IN.close()

#printing warnings for if the required variables are left blank
if cp_dir == '':
	print 'Fatal Warning: The location of Clinical Pathoscope (*Clinical_Pathoscope_directory) must be provided'
	fatal_errors += 1
if fastq_file == '':
	print 'Fatal Warning: You must provide a input fastq file (*filename)'
	fatal_errors += 1
if len(target_dbs) == 0:
	print 'Fatal Warning: You must provide a valid target_database (*Target_Databases)'
	fatal_errors += 1
if bowtie2_bin == '':	
	#print 'Fatal Warning: You must provide a valid bowtie2 bin directory (*bowtie2_bin)'
	print 'You did not provide a bowtie2 bin directory. If bowtie2 is not in your $PATH, Clinical Pathoscope will fail'
	#fatal_errors += 1
else:
	bowtie2_bin = '%s/' % bowtie2_bin
if db_dir == '' and usingPreloaded:
	print 'Fatal Warning: If you are using any of the preloaded databases(bacteria, human, virus), you must provide a valid directory of their location.'
	fatal_errors += 1
if len(host_filtration_dbs) == 0:
	print "Warning: No host filtration database was given; this may result in a higher number of false positives"
if len(filtration_dbs) == 0:
	print "Warning: No non-host filtration databases were given; this may result in a higher number of false positives"
if output_dir == '':
	cwd = os.getcwd()
	print "Warning: No output directory given"
	print "\tBy default results will be written to %s" % cwd
	output_dir = cwd
	
	
	
if fatal_errors > 0:
	print "Too many fatal errors: Exiting"
	sys.exit(1)
else:
	sample_name = fastq_file.split('/')[-1]
	sample_name = sample_name.replace('.fq','')
	sample_name = sample_name.replace('.fastq','')
	
print "Checking the length of the sequences in your fastq file\n"
split_seq = checkLength.checkLength(fastq_file,max_read_length)


#writing the shell script 
print "\nWriting the shell file as %s/run_clinical_pathoscope_%s.sh\n" % (output_dir,sample_name)

FILE_OUT = open('%s/run_clinical_pathoscope_%s.sh' % (output_dir,sample_name), 'w')

FILE_OUT.write("echo 'Running Clinical Pathoscope on sample %s'\n\n" % sample_name)

intermediate_files = ""
if split_seq:
	FILE_OUT.write("\necho 'Processing of the fastq file'\n")
	new_fastq = '%s/%s_processed.fastq' % (output_dir, sample_name)
	FILE_OUT.write("python %s/splitSequences.py %s %s %s 100\n" % (cp_dir, fastq_file, new_fastq, max_read_length) )
	intermediate_files += ('%s ' %new_fastq)
else:
	FILE_OUT.write("\necho 'No pre-processing of the fastq file is required'\n")
	new_fastq = fastq_file

#Mapping reads against the target database(s)
target_count = 0
sams_list = "" 	#will be a list of SAM files, one for each of the target databases
#target_dbs=a list of databases with full paths
for db in target_dbs:
	db_name = db.split('/')[-1]
	sam = "%s/%s_target%s.sam" %(output_dir, sample_name, target_count)

	FILE_OUT.write("\necho 'Aligning to the target database %s'\n" % db_name)
	FILE_OUT.write("%sbowtie2 %s -x %s -U %s -S %s -p %s %s\n" % (bowtie2_bin, bowtie2_quality, db, new_fastq, sam, num_threads, parameter) )

	sams_list += ('%s ' %sam)
	intermediate_files += ('%s ' %sam)
	target_count += 1

#Converting SAM files back to a single fastq file
new_fastq = '%s/%s_target_hits.fastq' % (output_dir, sample_name)

FILE_OUT.write("\necho 'Converting SAM back to Fastq'\n")
FILE_OUT.write("python %s/updatedFastq.py 1 %s 0 %s\n" % (cp_dir,new_fastq, sams_list))

intermediate_files += ('%s ' %new_fastq)

#Trimming reads for host-based alignment
FILE_OUT.write("\necho 'Cutting the reads down to 50 basepairs for host alignment'\n")
FILE_OUT.write("python %s/cutFastaSequences.py %s 50\n"  % (cp_dir, new_fastq) )

ret_new_fastq = new_fastq
cut_fastq = '%s/50_%s_target_hits.fastq' % (output_dir, sample_name)
intermediate_files += ('%s ' % cut_fastq)

#looping through the host_dbs
#for each host alignment 50bp reads are used 
host_count = 0
host_sam = ""
for db in host_filtration_dbs:
	db_name = db.split('/')[-1]
	sam = "%s/%s_host%s.sam" %(output_dir, sample_name, host_count)
	FILE_OUT.write("\necho 'Aligning to the host database %s'\n" % db_name)
	FILE_OUT.write("%sbowtie2 %s -x %s -U %s -S %s -p %s %s\n" % (bowtie2_bin, bowtie2_quality, db, cut_fastq, sam, num_threads, parameter))
	host_sam += ('%s ' %sam)
	intermediate_files += ('%s ' %sam)
	host_count += 1
	
if len(host_filtration_dbs) != 0:
	new_fastq = '%s/%s_nonHost0_hits.fastq' % (output_dir, sample_name)
	FILE_OUT.write("\necho 'Converting SAM file back to Fastq'\n")
	FILE_OUT.write("python %s/updatedFastq.py 0 %s 1 %s %s\n" %(cp_dir, new_fastq, ret_new_fastq, sam))
	intermediate_files += ('%s ' % new_fastq)

#looping through the remainder filter databases
sams_list = ""
filter_count = 0 
for db in filtration_dbs:
	db_name = db.split('/')[-1]
	sam = "%s/%s_filter%s.sam" %(output_dir, sample_name, filter_count)
	FILE_OUT.write("\necho 'Aligning to the target database %s'\n" % db_name)
	FILE_OUT.write("%sbowtie2 %s -x %s -U %s -S %s -p %s %s\n" % (bowtie2_bin, bowtie2_quality, db, new_fastq, sam, num_threads, parameter) )
	sams_list += ('%s ' %sam)
	intermediate_files += ('%s ' %sam)
	filter_count += 1

#Converting SAM files back to a single fastq file
if len(filtration_dbs) != 0:
	new_fastq = '%s/%s_nonFilter_hits.fastq' % (output_dir, sample_name)
	FILE_OUT.write("\necho 'Converting SAM back to Fastq'\n")
	FILE_OUT.write("python %s/updatedFastq.py 0 %s 0 %s\n" % (cp_dir, new_fastq, sams_list))
	intermediate_files += ('%s ' %new_fastq)

#Mapping reads against the target database(s)
target_count = 0
sams_list = "" 	#will be a list of SAM files, one for each of the target databases
#target_dbs=a list of databases with full paths
for db in target_dbs:
	db_name = db.split('/')[-1]
	sam = "%s/%s_target%s_2.sam" %(output_dir, sample_name, target_count)
	FILE_OUT.write("\necho 'Aligning to the target database %s'\n" % db_name)
	FILE_OUT.write("%sbowtie2 %s -x %s -U %s -S %s -p %s -k %s %s\n" % (bowtie2_bin, bowtie2_quality, db, new_fastq, sam, num_threads, bowtie2_k, parameter) )
	sams_list += ('%s ' %sam)
	intermediate_files += ('%s ' %sam)
	target_count += 1

if len(target_dbs) > 1:
	FILE_OUT.write("\necho 'Combining the sam files for the different target databases'\n")
	FILE_OUT.write("python %s/combineSams.py %s/%s_target_all2.sam %s\n" % (cp_dir, output_dir, sample_name, sams_list) )
	target_sam = '%s/%s_target_all2.sam' % (output_dir, sample_name)
	intermediate_files += ('%s ' %target_sam)
else:
	target_sam = '%s/%s_target0_2.sam' % (output_dir, sample_name)

FILE_OUT.write("\necho 'Running pathoscope on the sam file'\n")

FILE_OUT.write("python %s/pathoscope/pathoscope.py -t sam -f %s -e %s -outdir %s\n" % 
(cp_dir, target_sam, sample_name, output_dir) )

#if keep intermediate files is negative 
if not keep_int:
	FILE_OUT.write("\nrm %s" % intermediate_files)

FILE_OUT.write("\necho 'Finished!'\n")

FILE_OUT.close()

cline = 'sh %s/run_clinical_pathoscope_%s.sh' % (output_dir,sample_name)
os.system(cline)

