# This program pulls and reads a genbank file by command line input of accession number,
# then formats and writes the relevant information in bed format.

# Import adds modules to your script from the python argv
# argv = argument variable that holds the arguments you pass to your script when you run it
from sys import argv 

# Defining Accession Number, File_name, and Database
accession_number = argv[1] # Upacks argv-> assigned to 1 variable you can work with
file_name = accession_number + '.gbk'
ucsc_chrom='v'.join(accession_number.split('.'))
db = 'nucleotide' 
debug_parsing = 0

# Write Genbank File to BED file format: https://gist.github.com/brantfaircloth/893580
from Bio import SeqIO

import pdb

# Import regular expressions
import re

# for debugging output
import pprint
pp = pprint.PrettyPrinter(indent=0)

# Compile patterns for regular expressions
p = re.compile(r"""
    complement\(( # Start of a location
    .*)      # 0 or more(*) of anything(.)
    \)       # Trailing end parenthesis
    """, re.VERBOSE)

q = re.compile(r"""
    [0-9]+       # 1 or more(+) of any number
    \.\.         # .. \ denotes not anything (.)
    [0-9]+       # 1 or more(+) of any number
    """, re.VERBOSE)

q2 = re.compile(r"""
    ([0-9]+)       # 1 or more(+) of any number
    \.\.         # .. \ denotes not anything (.)
    ([0-9]+)       # 1 or more(+) of any number
    """, re.VERBOSE)

def loc_dict_to_exon_array(feature):
	loc=feature.location
	start = loc.start.position
	stop = loc.end.position
	if feature.strand < 0:
		strand = "-"
	else:
		strand = "+"
	loc_dict= { 'strand':strand, 'start':start, 'stop':stop}
	exon_array=[]
	exon_array.append(loc_dict)
	return exon_array
			

def genbank_to_dictionary():
	# add chrom name using split and join('v')
	ucsc_chrom='v'.join(accession_number.split('.'))

	# process features  within genome
	for record in SeqIO.parse(open(file_name, "rU"), "genbank") : #record is genome
		# get accession_number from record
		gene_dict={} # Initialize outermost dictionary
		count=0
		for feature in record.features: # record is genome
			# quit after Nth gene
			if feature.type == 'gene':
				# counter
				count+=1
				if debug_parsing and count>9:
					break



			if feature.type in ['gene','CDS','mRNA']:
				#
				# generic handling for any feature we support - setup or lookup entry in gene_dict	
				#
				try:
					gene_name=feature.qualifiers['gene'][0]
				except:
					# some features only have a locus tag
					gene_name = feature.qualifiers['locus_tag'][0]
				# Check to see if gene exits in dictionary
				if gene_name not in gene_dict: # if gene not in dict,
					gene_dict[gene_name]={'gene_name': gene_name, 'mRNA': [], 'CDS' :[] } # set dictionary and store gene_name to process later
					#gene_dict[gene_name]['gene_name']=gene_name
					# Add key-value pair {'mRNA':[]} to gene_def_dict to make format conistent and aid formatting later.
				# Set gene_dict to key-value pair {gene_name:gene_def_dict} 
				gene_def_dict = gene_dict[gene_name]

				# parse feature's location into an array of arrays of exon_defs
				loc_array=loc_dict_to_exon_array(feature)

				if debug_parsing: 
					print "\n---------- ", gene_name, feature.type, "----------"

				#
				# now feature type specific processing
				#
				if feature.type == 'gene':

					# call subroutine to convert location to array of dictionary
					#print (loc_dict_to_exon_array(feature.location))
					gene_def_dict['gene']=loc_array[0]								#start=gene_def_dict['gene']['start']
					#stop=gene_def_dict['gene']['stop']
					#strand=gene_def_dict['gene']['strand']
					#bed_line6 = ucsc_chrom + "\t{0}\t{1}\t{2}\t1000\t{3}\t".format(start, stop, gene_name, strand)
					#outf.write(bed_line6)
					if 'mRNA' not in gene_def_dict:
						gene_def_dict['mRNA']=[]
				# Could add similar if statement block for regulatory regions if helpful
				
				elif feature.type == 'CDS':
					gene_def_dict['CDS']=loc_array
				
				elif feature.type == 'mRNA':
					# Add key-value pair {feature_type:loc_array} to gene_def dictionary
					# Check to see if 'mRNA' is already a key in the dictionary
					print "mRNA: append to mRNA array"
					gene_def_dict['mRNA'].append(loc_array)

				if debug_parsing: 
					pp.pprint(gene_def_dict)
	#pp.pprint(gene_dict)
	if debug_parsing > 1: 
		quit(1)
	return gene_dict


# create the first 6 columns (easy) and columns 7/8 (more interesting)
def format_bed6_line(gene_def_dict): 
	
	# first 6 columns: 
	# how do i fix 'chrom','name', and 'score' without using variables in the function?
	# either make def more specific or call info outside of def and for loop, to later incoorporate
	return ucsc_chrom+'\t'+ gene_def_dict['gene'][0]['start']+'\t'+\
		gene_def_dict['gene'][0]['stop']+'\t'+gene_def_dict['gene_name']+'\t'+'score'+'\t'+\
		gene_def_dict['gene'][0]['strand']
	# how do i differentiate between CDS and genes or mRNA without a for loop or if statement?
	# nested calls to get values of dictionaries by dict[key]
	# str.join() is a similar function to split that will separate items by tab if i indicate column and delimeter

rgb='0,0,0'

# change gene_def_dict to gene_dict[key]
def write_gene_def_to_bed12(gene_def_dict):
	
	pp.pprint(gene_def_dict)
	# column 9:itemRgb
	score=1000
	item_rgb='0,0,0'
	# columns 7-8 thickStart and thickStop
	cds_def=gene_def_dict['CDS']
	cds_exon_count= len(cds_def)
	mrna_count=len(gene_def_dict['mRNA'])

	# default empty output
	mrna_ouputs = []

	#print 'CDS_count = '+str(cds_count)
	if cds_exon_count>0 :
		# compute blockCount    blockSizes  blockStarts
		mrna_ouput=[]
		mrna_ouputs=[]

		virtual_mrna_list = [cds_def] # list of CDS, where CDS is a list of exon_def's

		#print('----------cds_def------------------')
		#pp.pprint(cds_def)
		# when no mRNA is present (mrna_count=0), cds defines block size and start
		if mrna_count>0:
			virtual_mrna_list = gene_def_dict['mRNA']
		for mrna_def in virtual_mrna_list:
			block_count = len(mrna_def) # number of blocks for each mRNA
			# only apply the CDS to the mRNA's that completely contain it.
			# Does the CDS start and stop fall within the mRNA start and stop?
			# If not, then set thick start and stop to be mRNA start and stop.
			if cds_def[0]['start']<mrna_def[0]['start'] or cds_def[0]['stop']>mrna_def[block_count-1]['stop']:
				thick_start=mrna_def[0]['start']
				thick_stop=mrna_def[block_count-1]['stop']
			else:          
				thick_start = cds_def[0]['start']
				thick_stop = cds_def[cds_exon_count-1]['stop']
			thick_start_str=str(thick_start)
			thick_stop_str=str(thick_stop)

			bed6_str = ucsc_chrom+'\t'+ str(mrna_def[0]['start'])+'\t'+\
				str(mrna_def[block_count-1]['stop'])+'\t'+str(gene_def_dict['gene_name'])+'\t'+str(score)+'\t'+\
				str(mrna_def[0]['strand'])

			# If there are 2 mRNAs, we need to output 2 lines in the bed file
			# for m in range(0,mrna_count):
			#print "mrna_def"
			#pp.pprint(mrna_def)
			# create block size and block start lists
			block_sizes=[] # initialize array of integer sizes
			block_starts=[] # initialize array of integer starts
			for exon_def in mrna_def:
				#print "exon_def"
				#pp.pprint(exon_def)
				#print mrna_def[0]['start']
				block_size= str(int(exon_def['stop'])-int(exon_def['start']))
				block_sizes.append(block_size)
				block_start= str(int(exon_def['start'])-int(mrna_def[0]['start']))                
				block_starts.append(block_start)

			block_sizes_str=','.join(block_sizes)
			block_starts_str=','.join(block_starts)
			# format thickStart and thickEnd columns 7 and 8 and blocks
			mrna_ouput='\t'.join([bed6_str, thick_start_str, thick_stop_str, rgb, str(block_count), block_sizes_str, block_starts_str])
			mrna_ouputs.append(mrna_ouput)
	return '\n'.join(mrna_ouputs) 

def write_bed_12_line_to_bed_file(gene_dict):

	# Write the formatted information to a new bed file.
	bed_file= open('bed_file.bed','w') 
	# 'a' creates new file if it does not exist and does not truncate the file if it does exist
	# 'w' creates the file if the file does not exist, but it will truncate the existing file
	print(gene_dict.keys())
	for gene_name in gene_dict:
		print ('------gene_name=',gene_name,'--------')
		gene_def_dict = gene_dict[gene_name]
		print write_gene_def_to_bed12(gene_def_dict)  # pass definition for a gene to sub routine.
		bed_file.write(write_gene_def_to_bed12(gene_def_dict)+'\n')


	# Close the newly written bed file
	bed_file.close

if __name__ == '__main__':
	write_bed_12_line_to_bed_file(genbank_to_dictionary())
# Run with $ python genbank_to_bed.py NC_006273.2