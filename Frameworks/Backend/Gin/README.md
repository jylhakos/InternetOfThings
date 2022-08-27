# Go, Gin, MongoDB, React and Axios

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

## React

## Axios

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/InternetOfThings/Frameworks/Backend/Gin/framework.png?raw=true)

## References

Gin https://go.dev/doc/tutorial/web-service-gin

Go https://go.dev/ref/spec

Golang, MongoDB https://www.mongodb.com/languages/golang

MongoDB https://www.mongodb.com/docs/manual/tutorial

BSON https://www.mongodb.com/docs/drivers/go/current/fundamentals/bson/

Viper https://github.com/spf13/viper

JWT https://github.com/golang-jwt/jwt

