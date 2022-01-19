wtok:
	watchexec -cr "make tok"

tok: ..\examples\c4.ie
	type $<
	rem python tokenise.py $<
	rem python tokenise.py $< | python parse1-indent.py -
	python tokenise.py $< | python parse1-indent.py - | python parse2-syntax.py -

