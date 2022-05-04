package main

import (
	"fmt"
	"time"
)

func f(s string) {

	for i := 0; i < 5; i++ {

		time.Sleep(100 * time.Millisecond)

		fmt.Println(s)
	}
}

func main() {

	go f("World")

	f("Hello")
}
