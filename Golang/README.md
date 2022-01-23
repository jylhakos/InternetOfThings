# Golang

Golang is a language used for backend development.

**Download and install**

Click the button at [Go.dev/doc/install](https://go.dev/dl/go1.17.6.linux-amd64.tar.gz) to download the Go installer.

Extract Golang installer into /usr/local directory.

```

$ rm -rf /usr/local/go && tar -C /usr/local -xzf go1.17.6.linux-amd64.tar.gz

```
Set environment variables for GOLANG.

```
$ nano ~/.bashrc

```
Add export to GOPATH and GOROOT environment variables in the content of file, where GOPATH <WORKDIR> is directory for the projects.

```

$ export GOROOT=/usr/local/go

$ export GOPATH=<WORKDIR>

$ export PATH=$PATH:$GOROOT/bin:$GOPATH

$ go env

```
Reload .bashrc settings by source command.

```

$ source ~/.bashrc

```
**A program**

Create a directory for your Golang source code in <WORKDIR> directory.

```

$ mkdir <WORKDIR>/hello

$ cd hello

```
Run the go mod init <APP> command to enable dependencies in the <WORKDIR> directory.

```

$ go mod init hello

```
The content of go.mod file.

```

module hello

go 1.17

```
![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/go.png?raw=true)

Create hello.go file in which to write Golang code.

```

package main

import "fmt"

func main() {
    fmt.Println("Hello World")
}

```
Compile and run Golang program.

```

$ go run .

```

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/hello.png?raw=true)

**A module**

Create the package directory for a module.

```

$ mkdir greetings

```

```

package greetings

func Hello() string {
	return "Hello, World."
}

```
![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/greetings.png?raw=true)

Call your code from hello.go module with the path to the greetings module.

```

package main

import (
    "fmt"
    "hello/greetings"
)

func main() {
    message := greetings.Hello()
    fmt.Println(message)
}

```
Compile and install packages and dependencies.

```

$ go install

```

A link to Golang

https://go.dev/learn/