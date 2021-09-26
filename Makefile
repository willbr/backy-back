phony: watch

watch: src/*.c
	watchexec -cr "tcc -run src/main.c"
