# Defining Accession Number, File_name, and Database
accession_number= 'U00096'
file_name = accession_number + '.gbk'
db = 'nucleotide' 

#Write Genbank File to BED file format: https://gist.github.com/brantfaircloth/893580
from Bio import SeqIO

import pdb

def main():
    outf = open( accession_number +'.bed', 'w')
    header = """track name=accession_number  description="nucleotides" itemRgb=On\n"""
    outf.write(header)
    for record in SeqIO.parse(open(file_name, "rU"), "genbank") :
        for feature in record.features:
            if feature.type == 'gene':
                start = feature.location.start.position
                stop = feature.location.end.position
                try:
                    name = feature.qualifiers['gene'][0]
                except:
                    # some features only have a locus tag
                    name = feature.qualifiers['locus_tag'][0]
                if feature.strand < 0:
                    strand = "-"
                else:
                    strand = "+"
                bed_line = "cpdna\t{0}\t{1}\t{2}\t1000\t{3}\t{0}\t{1}\t65,105,225\n".format(start, stop, name, strand)
                outf.write(bed_line)
    outf.close()


if __name__ == '__main__':
    main()
	