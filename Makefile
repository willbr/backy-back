phony: watch

run: src/*.c
	#tcc -run src/main.c < src/tokens1.ie
	#tcc -run src/main.c < src/tokens2.ie
	tcc -run src/main.c < src/tokens3.ie

watch: src/*.c
	watchexec -cr "make run"
