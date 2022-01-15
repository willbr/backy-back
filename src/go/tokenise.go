package main

import (
    "bufio"
    "os"
    "fmt"
)

type state int

const (
    ready state = iota
    in_string
    in_word
)

func main() {
    input := bufio.NewScanner(os.Stdin)
    for input.Scan() {
        line := input.Text()
        fmt.Println("line:", len(line), line);
        //token := ""
        s := state(ready)

        fmt.Printf("e: %s\n", line[0:1])

        start_pos := 0
        for i, e := range line {
            //fmt.Printf("Char:%s Byte pos : %d, %t\n", string(e), i, e == ' ')
            switch s {
            case ready:
                switch e {
                case ' ':
                    fmt.Printf("space\n")
                default:
                    fmt.Printf("Char:%s Byte pos : %d, %t\n", string(e), i, e == ' ')
                }
            default:
            }
        }

        return
    }
}

