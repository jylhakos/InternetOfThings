package greetings

import "fmt"

func Hello(name string) string {
//func Hello() string {
    //return "Hello, World."
    message := fmt.Sprintf("Hello, %v", name)
    return message
}