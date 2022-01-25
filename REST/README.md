# RESTful API (REST)

The application consists of RESTful (Representational State Transfer) APIs with Golang and the Gin framework.

The goal of RESTful model is that a resource, for example a document, is transferred via client and server interactions.

The starting point for the RESTful model is using Hypertext Transfer Protocol (HTTP) as a transport system for remote interactions.

Each HTTP request from the client to the server contains all of the information necessary to complete the request.

A server will expose an endpoint at some Uniform Resource Identifier (URI).

A client then post to the endpoint a document containing the details of the request.

The server then will return a document giving the client that information.

**Project**

Go has its own package manager, and it is handled through the go.mod file.

$ go mod init <SERVICE>

go: creating new go.mod: module service/web-service

Create a file called main.go in the web-service directory. 

Define import modules in the main.go file.

```

import (

    "net/http"

    "github.com/gin-gonic/gin"
)

```

**Data structures**

Data is stored in a memory, but typically a program would interact with a database.

The tags such as json:<FIELD> specify a field’s name when the struct’s contents are serialized into JSON.

type field struct {
    <FIELD> string  `json:"<TAG>"`
}

var fields = [] field {
    {<FIELD>: "<CHARACTERS>"}, 
}

## HTTP

The application uses GET verb to request to retrieve a resource.

**GET**

The client makes a request at GET /notes, and you return all the notes as JSON data.

The gin.Context and  Context.JSON functions contain request details, and they are used to validate and serialize JSON data structures.

Use curl command to retrieve the full list of values from fields.

```

curl http://localhost:8000/notes \
    --header "Content-Type: application/json" \
    --request "GET"

```
![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/REST/HTTP_GET.png?raw=true)

A handler returns data from a GET request.

Use Context.Param to retrieve the id path parameter from the URL.

A loop iterates over the notes structs in the slice, looking for one whose ID field value matches the id parameter value.

If the id is found in the loop, then the program serializes that note struct to JSON and return it as a response with a 200 OK HTTP code.

Use curl command to make a request to the running web service.

```

$ curl http://localhost:8000/notes/2

```
![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/REST/HTTP_GET_ID.png?raw=true)

**POST**

The POST verb is used to submit the request to change state of a resource.

The Context.IndentedJSON serializes the data structure into JSON and adds it to the response.

```

func postNotes(c *gin.Context) {

    var newNote note

    if err := c.BindJSON(&newNote); err != nil {
        return
    }

    notes = append(notes, newNote)

    c.IndentedJSON(http.StatusCreated, newNote)
}

```
Use go get command to install Gin packages.

```

$ go get .

```
Compile and run main Go package with the below command.

```

$ go run .

```

Use Context.BindJSON to bind the request body to new data.

Append the data structure initialized from the JSON to the data slice.

Associate the POST method at the /<RESOURCE> path with the handler function.

Use curl command to make a request to the running web service.

```

$ curl http://localhost:8000/notes \
    --include \
    --header "Content-Type: application/json" \
    --request "POST" \
    --data '{"id": "4","content": "POST is used to add data to REST API","date": "2019-06-15T20:40:22.098Z","important": false}'

```
![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/REST/HTTP_POST.png?raw=true)

**OPTIONS**

The OPTIONS method requests describes permitted communication options for a given URL.

**CORS**

The same-origin restrictions to network requests prevent a client-side application running from one origin from obtaining data retrieved from another origin.

The CORS protocol consists of a set of headers that indicates whether a response can be shared cross-origin.

A browser first sends an `OPTIONS` request to a different domain than it is originated from a resource to validate that the resource is expecting requests from external source.

The `Origin` request header indicates where a request originates from.

Import Gin middleware from "github.com/gin-contrib/cors" to enable CORS and use Default() function to allow all origins.

CORS is a net/http handler implementing Cross Origin Resource Sharing in Golang.

An HTTP response to a CORS request can include the `Access-Control-Allow-Origin` headers.

```

func main() {

    router := gin.Default()

    router.Use(cors.Default())

    router.GET("/notes", getNotes)

    router.POST("/notes", postNotes)

    router.Run("localhost:8000")

```
Download and install cors from "github.com/gin-contrib/cors" repository.

```

$ go get .

```

A link to Golang Gin documents.

https://gin-gonic.com/docs/

