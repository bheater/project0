#Parsing Genbank Files

from Bio import SeqIO #Use SeqIO.read if there is only one genome (or sequence) in the file, and SeqIO.parse if there are multiple sequences. Since we're using genbank files, there typically (I think) only be a single giant sequence of the genome.
genome=SeqIO.read('U00096.gbk','genbank') #you MUST tell SeqIO what format is being read

print genome.features[:10] #prints a short description of the first ten features

#Feature Types
feats=set()
for feat in genome.features:
	feats.add(feat.type)

feats

#Feature Qualifiers
#Typical information will be 'product' (for genes), 'gene' (name) , and 'note' for misc. crap. Her's the qualifier dictionary for the first coding sequence (feature.type=='CDS'):

feat=genome.features[4]

feat.qualifiers

#How to use information from above in practice: 'product' and 'function' provide the current knowledge of what the gene (is thought to) make and what it (is thought to) do. 
predicted_genes=[]
for i,feature in enumerate(genome.features):
    if feature.type=='CDS':
        if 'product' in feature.qualifiers: #verify it codes for a real protein (not pseudogene)
            tot_genes+=1
            #data in qualifiers are all lists, even if only 1 string, so [0] converts to string
            #use lower() to make sure weirdly capitilized strings get selected as well
            product=feature.qualifiers['product'][0].lower()

            if product=='predicted protein':
                num_predicted+=1
                predicted_genes.append(feature)

#Grabbing the coding sequence
seq=feature.extract(genome.seq)
protein=seq.translate() #can also use optional switches like cds=True to raise errors if not a proper coding sequence (lacks start and stop codons)

sequence=feature.extract(genome.seq) # simple if you just want the gene sequence; works on antisense strand genes
#things get trickier if you want information outside of gene
location=feature.location
#position gives the actual python slice location of the start and end. need to reverse if on negative strand
#could use to get upstream or downstream regions
start=location.start.position
end=location.end.position

#Grabbing genomes from Genbank
from Bio import Entrez
#Replace with your real email 
Entrez.email = 'whatev@mail.com'
handle=Entrez.efetch(db='nucleotide',id='NC_009925',rettype='gb') # Accession id works, returns genbank format, looks in the 'nucleotide' database
#store locally
local_file=open('NC_009925','w')
local_file.write(handle.read())
handle.close()
local_file.close()
