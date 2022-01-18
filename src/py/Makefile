tok: ..\examples\c4.ie
	type $<
	rem python tokenise.py $<
	rem python tokenise.py $< | python parse2.py -
	python tokenise.py $< | python parse2.py - | python parse.py -

wtok:
	watchexec -cr "make tok"

