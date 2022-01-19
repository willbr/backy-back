wtok:
	watchexec -cr "make tok"

tok: ..\examples\c5.ie
	type $<
	rem python tokenise.py $<
	rem python tokenise.py $< | python parse1_indent.py -
	rem python tokenise.py $< | python parse1_indent.py - | python parse2_syntax.py -
	python tokenise.py $< | python parse1_indent.py - | python toco.py -

