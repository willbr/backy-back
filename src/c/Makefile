phony:

w:
	watchexec -cr "make tokens2"

tokens2: tokens2.c
	tcc -run $< ../examples/indent6.ie

