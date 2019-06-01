# coding: utf-8
# 生成双音节列表
# output: data/kata_romaji_double.txt

import codecs
vowels = [('ア', 'a'), ('イ', 'i'), ('ウ', 'u'), ('エ', 'e'), ('オ', 'o')]

def isLong(ro):
	if len(ro) >= 2:
		if ro[-1] == ro[-2]:
			return True
		else:
			return False
	else:
		return False

if __name__ == '__main__':
	ofile = codecs.open('data/kata_romaji_double.txt', mode='w', encoding='UTF-8')
	with codecs.open('data/kata_romaji.txt', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			line = line.strip('\n').strip('\r').split('\t')
			ka = line[0]
			ro = line[1]
			if not isLong(ro) and ro[-1] in 'aiueo':
				for k, v in vowels:
					if (v != ro[-1]):
						ofile.write(ka + k + '\t' + ro + v + '\n')
	ofile.close()