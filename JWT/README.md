# JSON Web Token (JWT)

JSON Web Token (JWT) can be sent through a URL to represent claims between two parties.

A signed token can verify the integrity of the claims contained within.

A client uses JWT for authorization to make requests to a server.

JWT consists of header, payload and signature.

A signature is generated using the header, payload and secret to verify the sent JWT in a request.

If the signature matches the one on the JWT, then the JWT is considered valid because without knowing the secret, there is no way to generate a valid signature.

Create main.go file and import JWT library module for authorization.

```

package main

import (
  "os"
  "https://github.com/golang-jwt/jwt"
)

```
Define a secret to export the secret key to an environment variable.

```

$ export SECRET=<SECRET>

```
Load a secret or a private key from the environment to Golang variable.

```

var secret = []byte(os.Getenv("SECRET"))

```
Creating, signing, and encoding a JWT token using the HMAC with SHA-256 algorithm method.

Claims are used to provide authentication to the party receiving the token.

Create an unsigned token from the claims and sign the token using a secret or private key. 

```

func createToken() (string, error) {

  token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
      "foo": "bar",
      "nbf": time.Date(2015, 10, 10, 12, 0, 0, 0, time.UTC).Unix(),
    })

  ss, err := token.SignedString(secretKey)

  return ss, err
}

```
The client sends POST request to login and receives a token or an error in a response.

```

$ curl -X POST http://localhost:8000/login -v

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

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/JWT/JWT.png?raw=true)