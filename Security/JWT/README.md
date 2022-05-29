# JWT

JSON Web Token (JWT) can be sent through a URL to represent claims between two parties.

A signed token can verify the integrity of the claims contained within.

A client uses JWT for authorization to make requests to a server.

JWT consists of header, payload and signature.

A signature is generated using the header, the payload and the secret to verify the sent JWT in a request.

If the signature matches the one on the JWT, then the JWT is considered valid because without knowing the secret, there is no way to generate a valid signature.

Create main.go file and import JWT library module for authorization.

```

package main

import (
  "os"
  "https://github.com/golang-jwt/jwt"
)

```
Define a secret to export the secret or a private key to an environment variable.

```

$ export SECRET=<SECRET>

```
Load a secret or a private key from the environment to Golang variable.

```

var secret = []byte(os.Getenv("SECRET"))

```
Creating, signing, and encoding a JWT token using the HMAC with SHA-256 algorithm method.

Claims are used to provide authentication to the party receiving the token.

Create an unsigned token from the claims and sign the token using the secret or a private key. 

```

func createToken() (string, error) {

  token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
      "foo": "bar",
      "nbf": time.Date(2015, 10, 10, 12, 0, 0, 0, time.UTC).Unix(),
    })

  ss, err := token.SignedString(secret)

  return ss, err
}

```
The client sends POST request to login and receives a token or an error in a response.

```

$ curl -v -X POST http://localhost:8000/login

```

The client sends JWT in the authorization header of the HTTP request to the API to authenticate the user in the server. 

The request to add resource includes the JWT, allowing the user to access resources that are permitted with that token.

```

$ curl http://localhost:8000/notes \
    --include \
    --header "Content-Type: application/json" \
    --header "Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb28iOiJiYXIiLCJuYmYiOi0yMjA4OTQ1NjAwfQ.SyFw8BLgdvSbGxnVbaDF5T1Yk9vBI8M6MJNaBHJ1MwQ" \
    --request "POST" \
    --data '{"id": "","content": "User authentication in Golang with JWT","date": "2019-08-25T01:20:23.098Z","important": false}'

```
You can verify a token at https://jwt.io/ web page.

**Login**

When the server receives login request, then the server can decode the username and password from the Authorization header.

If the request uses HTTP Basic Authentication, then BasicAuth function returns the username and password provided in the request's Authorization header.

If the credentials are not valid, then the server can return 401 Unauthorized response.

Extract the username and password from the request Authorization header by BasicAuth function.

```

$ curl -v -X POST \
  http://localhost:8000/login \
  -H 'content-type: application/json' \
  -d '{ "username": "anonymous", "password": "12345" }'

```
**React app**

The app has a login form on the top of the page.

The app state has fields for username and password to store the data from the form.

The form fields have an event handler to synchronize changes in the field to the state of the App component.

The app uses an HTTP POST method to send username and password in the request to the login endpoint of REST API to create resource on the server.

If the login is successful then a token and the user details extracted from the server response is saved to the application's state.

The value of token can be changed with a function setToken and the token is stored in the browser's local storage.

The token is set to the Authorization header as third parameter of the post method in Axios.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)
