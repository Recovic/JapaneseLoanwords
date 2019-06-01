# coding: UTF-8
# 处理转换表中的促音和长音

vowel = ['a', 'i', 'u', 'e', 'o']
consonant = ['k', 's', 't', 'c', 'h', 'g', 'z', 'j', 'd', 'b', 'p', 'v', 'f']
# only count if the consonant has tsu tone

import codecs

with codecs.open('../data/kata_romaji2.txt', encoding='UTF-8') as file:
	with codecs.open('../data/kata_romaji22.txt', mode='w', encoding='UTF-8') as outfile:
		for line in file.readlines():
			line = line.strip("\n")
			pair = line.split('\t')
			kata = pair[0]
			roma = pair[1]

			# long tone
			if roma[-1] in vowel:
				outfile.write(kata + 'ー' + '\t' + roma + roma[-1] + '\n')

			# tsu
			if roma[0] in consonant:
				if roma[0:2] == 'ch':  # When it comes to 'ch', the rule is special.
					outfile.write('ッ' + kata + '\t' + 't' + roma + '\n')
				else:
					outfile.write('ッ' + kata + '\t' + roma[0] + roma + '\n')

			# both long tone and tsu tone
			if roma[-1] in vowel and roma[0] in consonant:
				if roma[0:2] == 'ch':  # When it comes to 'ch', the rule is special.
					outfile.write('ッ' + kata + 'ー' + '\t' + 't' + roma + roma[-1] + '\n')
				else:
					outfile.write('ッ' + kata + 'ー' + '\t' + roma[0] + roma + roma[-1] + '\n')

