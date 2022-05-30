package main

import (
    "fmt"
    "hello/greetings"
)

func main() {
    //fmt.Println("Hello, World!")
    //message := greetings.Hello()
    message := greetings.Hello("World")
    fmt.Println(message)
}