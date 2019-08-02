#!/bin/bash


while getopts :o:f: OPT; do
    case $OPT in
	o|+o)
	    OUT_PREFIX=${OPTARG};;
	f|+f)
	    FILTER=${OPTARG};;
	*)
	    echo "usage: `basename $0` -o OUTPUT_PREFIX -f DECOY_FILTER_FASTA REF_FASTA1 [REF_FASTA2, REF_FASTA3, ...]"
	    exit 2
    esac
done
shift `expr $OPTIND - 1`
OPTIND=1

if [ -z $FILTER ]; then
    echo "WARNING: No filter file provided" 1>&2
else
    FILTER_FILE=$(readlink -f $FILTER)
fi

if [ -z $OUT_PREFIX ]; then
    echo "FATAL: no out put"
fi

if [ -e $OUT_PREFIX.fasta ]; then
    echo "FATAL: writing to existing file $f" 1>&2
    exit 1
fi

FASTA_FILES=$@
if [ -z $FASTA_FILES ]; then
   echo "FATAL: no input fasta files" 1>&2
   exit 1
fi

for f in $FASTA_FILES;
do
    if [ ! -e $f ]; then
	echo "FATAL: cannot find file $f" 1>&2
	exit 1
    fi
done

counter=0

echo "======================Renameing the species=============================="
echo -e "species\tID" > ${OUT_PREFIX}.speciesID.txt

for f in $FASTA_FILES; 
do
    counter=$((counter+1))
    ti=$(printf %04d $counter)
    sed "s/>/>ti|$ti|gi|$ti|/"  $f >>$OUT_PREFIX.fasta
    echo -e "$f\t$ti" >>${OUT_PREFIX}.speciesID.txt
done

echo "=====================Building bowtie2 index=============================="
bowtie2-build $OUT_PREFIX.fasta $OUT_PREFIX
samtools faidx $OUT_PREFIX.fasta
bedtools makewindows -g $OUT_PREFIX.fasta.fai  -w 10000 > $OUT_PREFIX.10kbWin.bed

echo "=================Writing bpipe configuration file========================"
OUT_FILE=$(readlink -f $OUT_PREFIX.fasta)
OUT_DIR=${OUT_FILE%/*}
FILTER_DIR=${FILTER_FILE%/*}
WINDOWS_FILE=$(readlink -f $OUT_PREFIX.10kbWin.bed)

echo "REF=\"$OUT_FILE\"" > pathoscope.bconfig
echo "REF_DIR=\"$OUT_DIR\"" >>pathoscope.bconfig
echo "FILTER=\"$FILTER_FILE\"" >>pathoscope.bconfig
echo "FILTER_DIR=\"$FILTER_DIR\"" >>pathoscope.bconfig
echo "NUM_SPECIES=$counter" >>pathoscope.bconfig
echo "WINDOWS_BED=\"$WINDOWS_FILE\"" >> pathoscope.bconfig
