phony: watch run test1 test2 test3

test1: .\src\tokens1.ie
	type $<
	tcc -run src/main.c < $<
	tcc -run src/main.c < $< | python src/transform.py
	tcc -run src/main.c < $< | python src/transform.py | python src/eval.py

test2: .\src\tokens2.ie
	type $<
	tcc -run src/main.c < $<
	tcc -run src/main.c < $< | python src/transform.py
	tcc -run src/main.c < $< | python src/transform.py | python src/eval.py

test3: .\src\tokens3.ie
	type $<
	tcc -run src/main.c < $<
	tcc -run src/main.c < $< | python src/transform.py
	tcc -run src/main.c < $< | python src/transform.py | python src/eval.py

test4: .\src\tokens4.ie
	type $<
	tcc -run src/main.c < $<
	tcc -run src/main.c < $< | python src/transform.py
	tcc -run src/main.c < $< | python src/transform.py | python src/eval.py

test5: .\src\tokens5.ie
	type $<
	tcc -run src/main.c < $<
	tcc -run src/main.c < $< | python src/transform.py
	tcc -run src/main.c < $< | python src/transform.py | python src/eval.py

alt:
	python src/alt.py --echo-code
	python src/alt.py | python src/eval.py --trace

run: src/*.c src/*.py alt

watch:
	watchexec -cr "make run"

