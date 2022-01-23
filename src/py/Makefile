wtok:
	watchexec -cr "make tok"

tok: ../examples/c6.ie
	# type $<
	#echo.
	#rem python tokenise.py $<
	#rem python tokenise.py $< | python parse1_indent.py -
	#rem python tokenise.py $< | python parse1_indent.py - | python parse2_syntax.py -
	#echo.
	python3 tokenise.py $< | python3 parse1_indent.py - | python3 toco.py -

