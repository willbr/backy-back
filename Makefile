phony: watch run test1 test2 test3

test0: .\src\tokens2.ie
	type $<
	tcc -Wall -run src/tokeniser.c - < $<
	tcc -run src/tokeniser.c - < $< | python src/eval.py
	tcc -run src/tokeniser.c - < $< | tcc -run src/eval.c

test1: .\src\tokens1.ie
	type $<
	tcc -Wall -run src/tokeniser.c - < $<
	tcc -run src/tokeniser.c - < $< | python src/eval.py

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

alt2: .\src\tokens0.ie src/*.py
	type $<
	python src/alt2.py --echo-code < $<

walt2:
	watchexec -cr "make alt2"

alt3: .\src\tokens5.ie src/*.py
	type $<
	python src/alt3.py $<

walt3:
	watchexec -cr "make alt3"

alt4: .\src\c2.ie src/*.py
	type $<
	rem python src/alt4.py --wrap-everything $<
	python src/alt4.py --wrap-everything $< | python src/c-printer.py -

walt4:
	watchexec -cr "make alt4"

run: src/*.c src/*.py test0

test-py: src/*.py
	python -m unittest src/test-eval.py -f

wtest-py:
	watchexec -cr "make test-py"

watch:
	watchexec -cr "make run"

