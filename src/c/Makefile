phony:

f=..\examples\indent7.ie
f=..\examples\c1.ie

w:
	watchexec -cr "make tokens2"

tokens2: tokens2.c
	type $f
	tcc -run $< $f

