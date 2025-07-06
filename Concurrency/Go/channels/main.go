package main

import "fmt"

func f(s chan string) {

	for i := 0; i < 5; i++ {

		message := <- s
		
		fmt.Println(message)

		s <- "World"
	}
}

func main() {

	s := make(chan string)

	go f(s)

	for i := 0; i < 5; i++ {

		s <- "Hello"

		message := <- s
		
		fmt.Println(message)
   }
}