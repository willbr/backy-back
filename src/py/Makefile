wtok:
	watchexec -cr "make tok"

tok: ../examples/c7.ie
## type $<
##echo.
##rem python tokenise.py $<
#python tokenise.py $< | python parse1_indent.py -
	python tokenise.py $< | python parse1_indent.py - | python parse2_syntax.py -
##echo.
	python tokenise.py $< | python parse1_indent.py - | python toco.py -

tok_errors: ../examples/tokenise_errors_01.ie
	python tokenise.py $< | python parse1_indent.py - | python parse2_syntax.py -

