phony:

w:
	watchexec -cr "make tokens2"

tokens2: tokens2.c
	tcc -run $< ../examples/c0.ie

