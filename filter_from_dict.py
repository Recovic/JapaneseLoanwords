# coding: utf-8
# 从日英词典中筛选音译词

import codecs
import chunk

alpha = 0.7
# 若编辑距离大于 alpha*len，则丢弃该候选

if __name__ == '__main__':
	chunk.init()
	with codecs.open('data/dictionary_filter.txt', mode='w', encoding='UTF-8') as outfile:
		with codecs.open('data/dictionary.txt', mode='r', encoding='UTF-8') as file:
			for line in file.readlines():
				line = line.strip('\n')
				line = line.strip('\r')
				line = line.split(',')
				en = line[0]
				ja = line[1]
				ro = chunk.ka2ro(ja)
				d = chunk.levdis.getDisMatrix(en, ro)
				l = max(len(en), len(ro))
				if d[-1][-1] < alpha * l:
					outfile.write(en + ',' + ja + '\n')
