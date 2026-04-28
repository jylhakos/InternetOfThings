# Go, Gin, Gorm, MongoDB, PostgreSQL

Go web frameworks such as Gin, Fiber, and Echo provide fast routing, middleware support, and JSON handling for building REST APIs and microservices.

## Basics of Go

After running the commands below, your Go project should be initialized, committed to Git, and pushed to your GitHub repository.

Here is how to initialize a new Go project and commit it to a GitHub repository using the `go mod init` command.

### 1. Create a new directory

```bash
$ mkdir <project_name>
$ cd <project_name>
```

### 2. Initialize a Go module

```bash
$ go mod init <project_name>
```

Replace `<project_name>` with your desired project name (e.g., `my-go-app`).

The `go mod init` command creates a `go.mod` file which tracks the project's dependencies.

### 3. Create your Go files

Create your `main.go` file, or any other Go files you need.

### 4. Initialize a Git repository

```bash
$ git init
```

The `git init` command initializes a new Git repository in your project's root directory.

### 5. Add your files

```bash
$ git add .
```

The `git add .` command stages all files in your project for commit. You can also use `git add <file_name>` to add individual files.

### 6. Commit your changes

```bash
$ git commit -m "Initial commit"
```

The `git commit` command commits your staged changes with the message "Initial commit".

### 7. Create a new repository on GitHub

Go to GitHub and create a new repository with the same name as your project (`<project_name>`).

### 8. Add the remote repository

```bash
$ git remote add origin <repository_url>
```

Replace `<repository_url>` with the URL you copied from GitHub.

### 9. Rename the branch to main

```bash
$ git branch -M main
```

### 10. Push the changes to GitHub

```bash
$ git push -u origin main
```

The `git push` command pushes your local commits to the remote repository on GitHub.

## Go

Use go get command to add the github.com/gin-gonic/gin etc. modules as a dependency for your module.

```

$ go get .

```

## Gin

Gin is a web framework written in Golang (Go).

An incoming HTTP request can be handled by a chain of middlewares.

Gin can parse and validate the content of JSON from a request

Install and import Gin in your code.

```

$ go get github.com/gin-gonic/gin

```

## Environment Variables

```

$ go get github.com/spf13/viper

```

## MongoDB

You can start the mongod process by issuing the following command.

```

$ sudo systemctl start mongod

```


```

$ go get go.mongodb.org/mongo-driver/mongo

```
## Functions

The functions with names that start with an uppercase letter (Camel case) will be exported to other packages. 

If the function name starts with a lowercase letter, it won't be exported to other packages.

If the function name consists of multiple words, each word after the first word should be capitalized.

## BSON

The process of converting Golang value to BSON is called marshalling, while the reverse process is called unmarshalling.

## JWT

JWT (JSON Web Token) token is a cryptographically signed token which the server generates and sends to the client. 

JWT consists of three parts which are header, payload and signature.

An access token is used for authenticating the requests sent to the server and a client uses JWT for making requests to the server.

To verify a JWT, the server generates the signature once again using the header and payload from the incoming JWT, and its secret key.

If the newly generated signature matches the one on the JWT, then the JWT is considered valid.

```

$ go get github.com/golang-jwt/jwt/v4

```

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Frameworks/Backend/Gin/albums.png?raw=true)

Figure: REST methods and CRUD operations

## References

How to write Go code https://go.dev/doc/code

Gin https://go.dev/doc/tutorial/web-service-gin

Go https://go.dev/ref/spec

Golang, MongoDB https://www.mongodb.com/languages/golang

MongoDB https://www.mongodb.com/docs/manual/tutorial

BSON https://www.mongodb.com/docs/drivers/go/current/fundamentals/bson/

Viper https://github.com/spf13/viper

JWT https://github.com/golang-jwt/jwt

