import os, sys, gzip

def iopen(inpath):
	""" Open input file for reading regardless of compression [gzip, bzip] or python version """
	ext = inpath.split('.')[-1]
	# Python2
	if sys.version_info[0] == 2:
		if ext == 'gz': return gzip.open(inpath)
		elif ext == 'bz2': return bz2.BZ2File(inpath)
		else: return open(inpath)
	# Python3
	elif sys.version_info[0] == 3:
		if ext == 'gz': return io.TextIOWrapper(gzip.open(inpath))
		elif ext == 'bz2': return bz2.BZ2File(inpath)
		else: return open(inpath)

def readfq(fp):
	""" A generator function for parsing fasta/fastq records """
	last = None # this is a buffer keeping the last unprocessed line
	while True: # mimic closure; is it a bad idea?
		if not last: # the first record or a record following a fastq
			for l in fp: # search for the start of the next record
				if l[0] in '>@': # fasta/q header line
					last = l[:-1] # save this line
					break
		if not last: break
		name, seqs, last = last[1:].partition(" ")[0], [], None
		for l in fp: # read the sequence
			if l[0] in '@+>':
				last = l[:-1]
				break
			seqs.append(l[:-1])
		if not last or last[0] != '+': # this is a fasta record
			yield name, ''.join(seqs), None # yield a fasta record
			if not last: break
		else: # this is a fastq record
			seq, leng, seqs = ''.join(seqs), 0, []
			for l in fp: # read the quality
				seqs.append(l[:-1])
				leng += len(l) - 1
				if leng >= len(seq): # have read enough quality
					last = None
					yield name, seq, ''.join(seqs); # yield a fastq record
					break
			if last: # reach EOF before reading enough quality
				yield name, seq, None # yield a fasta record instead
				break

if __name__ == "__main__":

	infile = iopen(sys.argv[1])
	max_reads = int(sys.argv[2])
	index = 0
	for name, seq, qual in readfq(infile):
		sys.stdout.write('>%s\n%s\n' % (name, seq))
		index += 1
		if index == max_reads: break



