
ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
    detected_OS := Windows
	PATH := $(PATH);./bin/
	mkdir = mkdir
	make = make
	rm = del
	EXE = .exe
	ignore := rem
else
    detected_OS := $(shell uname)  # same as "uname -s"
	PATH := $(PATH):./bin/
	mkdir = mkdir
	make = make
	rm = rm
	EXE =
	ignore := echo ignore
endif


bb-tests:
	bb src/script.txt

wbbt:
	watchexec -cr "make bb-tests"

toco-tests:
	toco src/examples/c0.ie
	toco src/examples/c1.ie
	toco src/examples/c2.ie
	toco src/examples/c3.ie
	toco src/examples/c4.ie
	$(ignore) parse_ie src\examples\c5.ie
	toco src/examples/c5.ie
	toco src/examples/c6.ie
	toco src/examples/c7.ie
	toco src/examples/c8.ie
	toco src/examples/c9.ie

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

alt4: .\src\c4.ie src/*.py
	type $<
	rem python src/alt4.py --wrap-everything $<
	python src/alt4.py --wrap-everything $< | python src/c-printer.py -

walt4:
	watchexec -cr "make alt4"

run: src/*.c
	tcc -run src/parse.c

test-c:
	python src/py/test-c.py

wtest-c:
	watchexec -cr "make test-c"

test-py: src/py/*.py
	python -m unittest src/test-eval.py -f

wtest-py:
	watchexec -cr "make test-py"

pparse:
	python src/py/pluck-test.py 3 | tcc -run src/c/parse.c - | python src/py/parse.py

wpparse:
	watchexec -cr "make pparse"

eval:
	python src/py/pluck-test.py 3 | tcc -run src/c/parse.c - | python src/py/eval.py

weval:
	watchexec -cr "make eval"

toco: src\examples\c4.ie
	type $<
	rem type $< | tcc -run src/c/parse.c -
	rem type $< | tcc -run src/c/parse.c - | python src/py/parse.py
	type $< | tcc -run src/c/parse.c - | python src/py/toco.py

wtoco:
	watchexec -cr "make toco"

simple: src\examples\tokens3.ie
	type $<
	type $< | tcc -run src/c/simple-tokens.c -
	type $< | tcc -run src/c/simple-tokens.c - | python src/py/parse.py
	rem type $< | tcc -run src/c/simple-tokens.c - | python src/py/toco.py

wsimple:
	watchexec -cr "make simple"

indent: src\examples\indent2.ie
	type $<
	rem type $< | tcc -run src/c/simple-tokens.c -
	type $< | tcc -run src/c/simple-tokens.c - | python src/py/parse.py

windent:
	watchexec -cr "make indent"

watch:
	watchexec -cr "make run"

pytok: src\examples\c4.ie
	type $<
	rem python src/py/tokenise.py $<
	rem python src/py/tokenise.py $< | python src/py/parse2.py -
	python src/py/tokenise.py $< | python src/py/parse2.py - | python src/py/parse.py
	python src/py/tokenise.py $< | python src/py/parse2.py - | python src/py/toco.py

wpytok:
	watchexec -cr "make pytok"

alt:
	python src\alt.py src\script.txt

walt:
	watchexec -cr "make alt"

