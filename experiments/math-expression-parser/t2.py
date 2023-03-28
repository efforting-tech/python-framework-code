#This rabbit hole deals with the idea of spatial parsing

from tt1 import math_tokenizer

from efforting.mvp4.text_processing import expand_tabs

example = expand_tabs('''

		⎡ 0   -k.z  k.y⎤
	K =	⎢ k.z  0   -k.x⎥
		⎣-k.y  k.x  0  ⎦

''')


#Step one could be to identify matching brackets and how they connect
#To test this we want to define a test tokenizer

for t in math_tokenizer.tokenize(example):
	print(t)