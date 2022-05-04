package main

import (
	"fmt"
	"sync"
)

func f(s string) {

	for i := 0; i < 5; i++ {

		fmt.Println(s)
	}
}

func main() {

	wg := sync.WaitGroup{}

	wg.Add(1)

	go func() {
		f("World")
		defer wg.Done()
    }()

    f("Hello")

	wg.Wait()
}