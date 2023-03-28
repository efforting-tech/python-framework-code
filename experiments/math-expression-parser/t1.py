
#from efforting.mvp4.






math_tokenizer = tokenizer('math_tokenizer',
	(literal('+'),		yield_match(CL.plus)),
	(literal('-'),		yield_match(CL.plus)),
	(literal('*'),		yield_match(CL.plus)),
	(literal('·'),		yield_match(CL.plus)),
	(literal('×'),		yield_match(CL.plus)),
	(literal('/'),		yield_match(CL.plus)),
	(literal('<'),		yield_match(CL.plus)),
	(literal('>'),		yield_match(CL.plus)),
	(literal('/'),		yield_match(CL.plus)),


)

'''



	√
	∛
	∜ 	∝ 	∞

+
-
*
·
×
/
<
>
/


'''

