ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
    detected_OS := Windows
	PATH := $(PATH);./bin/
	mkdir = mkdir
	make = make
	rm = del
	EXE = .exe
	ignore := rem
	python := python
	cat := type
else
    detected_OS := $(shell uname)  # same as "uname -s"
	PATH := $(PATH):./bin/
	mkdir = mkdir
	make = make
	rm = rm
	cat := cat
	EXE =
	ignore := echo ignore
	python := python3
endif

wtok:
	watchexec -cr "make tok"

tok: ../examples/tokens15.ie
	$(cat) $<
#	$(python) tokenise.py $<
#	$(python) parse1_indent.py $<
#	$(python) parse2_syntax.py $<
	$(python) ie.py $<

tok_errors: ../examples/tokenise_errors_01.ie
	python tokenise.py $< | python parse1_indent.py - | python parse2_syntax.py -

