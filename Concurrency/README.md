# Concurrency

Concurrent execution alternates doing a little of each task until all tasks are completed.

Concurrency in Golang is the ability for functions to run independent of each other.

## Goroutines

Goroutine is a function that runs concurrently with other functions.

When to use Goroutines in GoLang?

* Running background operations in a program.

* Making multiple requests to different API endpoints.

* A task can be split into different segments.

Code that runs in a goroutine can run concurrently with other code.

The evaluation of f, x, y, and z happens in the current goroutine and the execution of f happens in the new goroutine.

Use the go keyword followed by the function to create goroutines.

```

go f(x, y, z)

```

The main function doesn’t wait before Goroutines get a chance to execute until the program uses the sleep method.

### Synchronization

Goroutines run in the same address space, therefore access to shared memory must be synchronized.

If goroutines share no data, then the program needn’t synchronizing.

WaitGroup is used to wait for the program to finish goroutines.

```

package main

import (
    "fmt"
    "sync"
)
 
func main() {
 
    wg := sync.WaitGroup{}

    wg.Add(1)
 
    go print(&wg)
 
 	fmt.Println("Hello")

    wg.Wait()
}
 
func print(wg *sync.WaitGroup) {

    fmt.Println("World")

    wg.Done()
}

```
## Channels

Channels act as a data transfer pipe that Goroutines can either send to or read from the pipe.

When the program sends data into the channel using Goroutines, it will be blocked until the data is consumed by another Goroutines.

The <- operator specifies the channel direction, send or receive.

```

package main

import "fmt"

func f(c chan string) {

	message := <-c

	fmt.Println("Hello", message)
}

func main() {

	c := make(chan string)

	go f(c)

	c <- "World"
}


```

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Concurrency/goroutines.png?raw=true)

Figure: Goroutines (G) are taking turns in a local queue (LRQ) sharing their thread (M) that runs on a processor (P).