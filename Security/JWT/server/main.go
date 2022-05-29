package main

import (

  "fmt"

  "os"

  "time"

  //"strconv"

  "strings"

  "net/http"

  "errors"

  "github.com/google/uuid"

  "github.com/gin-gonic/gin"
                                                         
  "github.com/gin-contrib/cors"

  "github.com/golang-jwt/jwt"

)

type Note struct {
    ID        string `json:"id"`
    Content   string  `json:"content"`
    Date      string  `json:"date"`
    Important bool  `json:"important"`
}

var notes = [] Note {
    { ID: uuid.New().String(), Content: "Browser can execute only Javascript", Date: "2019-05-30T17:30:31.098Z", Important: true },
    { ID: uuid.New().String(), Content: "GET and POST are important methods of HTTP protocol", Date: "2019-05-30T18:39:34.091Z", Important: false },
    { ID: uuid.New().String(), Content: "The Principles of Object-Oriented JavaScript", Date: "2019-05-30T19:20:14.298Z", Important: true },
}

var secret = []byte(os.Getenv("SECRET"))

type Claims struct {
  ID uint64 `json:"id"`
  Username string `json:"username"`
  Password string `json:"password"`
}

type Login struct {
  Username  string `json:"username"`
  Password  string `json:"password"`
}

var users = map[string]string{
  "username": "password",
}

func createToken() (string, error) {

  token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims {
          "foo": "bar",
          "nbf": time.Date(1900, 01, 01, 12, 0, 0, 0, time.UTC).Unix(),
        })

  ss, err := token.SignedString(secret)

  fmt.Println(secret, ss, err)

  if err != nil {

    fmt.Errorf("Error: %s", err.Error())

    return "", err
  }

  return ss, nil
}

func validateToken(c *gin.Context) (*jwt.Token, error) {

  ss := strings.Split(c.Request.Header["Authorization"][0], " ")[1]

  fmt.Println(ss)

  //token, err := jwt.ParseWithClaims(ss, &Claims{}, func(token *jwt.Token) (interface{}, error) {
  //    return []byte(secret), nil
  //})

  token, err := jwt.Parse(ss, func(token *jwt.Token) (interface{}, error) {

    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {

      return nil, errors.New("Error")
    }

      return []byte(secret), nil
    })

    if err != nil {

      return nil, err
    }

  fmt.Println(token)

  return token, nil
}

func login(c *gin.Context) {

  var json Login

  if err := c.ShouldBindJSON(&json); err != nil {
    c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
    return
  }

  if json.Username != "anonymous" || json.Password != "12345" {
    c.JSON(http.StatusUnauthorized, gin.H{"status": "unauthorized"})
    return
  }

  token, err := createToken()

  if err != nil {

     return
  }

  c.JSON(http.StatusOK, gin.H{"token": token})

  //c.JSON(http.StatusOK, token)
}

func getNotes(c *gin.Context) {

    c.IndentedJSON(http.StatusOK, notes)
}

func getNoteByID(c *gin.Context) {

    id := c.Param("id")

    for _, note := range notes {

        if note.ID == id {

            c.IndentedJSON(http.StatusOK, note)

            return
        }
    }

    c.IndentedJSON(http.StatusNotFound, gin.H{"message": "A note is not found."})
}

func postNotes(c *gin.Context) {

    token, err := validateToken(c)

    if (token == nil) {

      c.IndentedJSON(http.StatusUnauthorized, gin.H{"status": http.StatusUnauthorized, "message": "Un Authorized"})

      return
    }

    if err != nil {

      fmt.Println(err)
      
      c.JSON(http.StatusBadRequest, gin.H{"status": http.StatusBadRequest, "message": "Bad Request"})
      
      return
    }

    var newNote Note

    if err := c.BindJSON(&newNote); err != nil {
      return
    }

    //var notes_length = len(notes)

    newNote.ID = uuid.New().String()

    fmt.Println("uuid.UUID", newNote.ID)

    //newNote.ID = strconv.Itoa(notes_length + 1)

    notes = append(notes, newNote)

    fmt.Println(notes)

    c.IndentedJSON(http.StatusCreated, newNote)
}

func main() {

  router := gin.Default()

  router.Use(cors.Default())

  router.StaticFile("/favicon.ico", "./public/favicon.ico")

  router.LoadHTMLGlob("./public/*.html")

  router.GET("/", func(c *gin.Context) {

      c.HTML(http.StatusOK, "index.html", nil)
  })

  router.POST("/login", login)

  router.GET("/notes", getNotes)

  router.GET("/notes/:id", getNoteByID)

  router.POST("/notes", postNotes)

  router.Run("localhost:8000")

}