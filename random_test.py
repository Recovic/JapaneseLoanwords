# coding: utf-8
# 随机抽取测试数据

import codecs
import random

if __name__ == '__main__':
	random_lst = random.sample(range(1, 1741), 100)
	s = set(random_lst)
	count = 0
	ofile = codecs.open('data/test_chunked2.data', mode='w', encoding='UTF-8')
	with codecs.open('data/test_chunked.data', mode='r', encoding='UTF-8') as file:
		for line in file.readlines():
			count += 1
			if count in s:
				ofile.write(line)
	ofile.close()


