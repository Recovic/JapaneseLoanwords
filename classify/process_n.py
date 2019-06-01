# coding: utf-8

import codecs

ofile = codecs.open("kata_romaji_n.txt", mode='w', encoding='utf-8')

with codecs.open('../data/kata_romaji.txt', mode='r', encoding='utf-8') as file:
	for line in file.readlines():
		line = line.strip('\n').strip('\r')
		line = line.split('\t')
		if not line:
			break
		ja = line[0]
		en = line[1]
		if ja[0] != 'ッ' and ja[-1] != 'ー':
			ofile.write(ja + 'ン' + '\t' + en + 'n' + '\n')


ofile.close()
