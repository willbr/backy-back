double
    \ 1

double newline indent dedent 1 newline


[double newline 1]



puts newline indent dedent ( "hello " vim+ "world" )



line-continuation
backslash



puts ie\newline ie\indent ie\backslash ( "hello " + "word" )


a ie\newline ie\indent b ie\newline ie\indent c ie\newline
[a ie\newline [b ie\newline [c ie\newline]]]
[a [b [c]]]

a ie\newline ie\indent b ie\newline c ie\newline
[a ie\newline [b ie\newline] [c ie\newline]]
[a [b] [c]]

