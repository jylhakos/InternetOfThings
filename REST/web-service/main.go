package main

import (

	"net/http"

	"github.com/gin-gonic/gin"
)

type note struct {
	ID			string  `json:"id"`
    Content		string  `json:"content"`
    Date		string  `json:"date"`
    Important	bool 	`json:"important"`
}

var notes = [] note {
    { ID: "1", Content: "Browser can execute only Javascript", Date: "2019-05-30T17:30:31.098Z", Important: true },
    { ID: "2", Content: "GET and POST are important methods of HTTP protocol", Date: "2019-05-30T18:39:34.091Z", Important: false },
    { ID: "3", Content: "A proper dinosaur codes with Java", Date: "2019-05-30T19:20:14.298Z", Important: true },
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

    var newNote note

    if err := c.BindJSON(&newNote); err != nil {
        return
    }

    notes = append(notes, newNote)

    c.IndentedJSON(http.StatusCreated, newNote)
}

func main() {

	router := gin.Default()

	router.StaticFile("/favicon.ico", "./public/favicon.ico")

	router.LoadHTMLGlob("./public/*.html")

    router.GET("/", func(c *gin.Context) {
        c.HTML(http.StatusOK, "index.html", nil)
    })

    router.GET("/notes", getNotes)

    router.GET("/notes/:id", getNoteByID)

    router.POST("/notes", postNotes)

    router.Run("localhost:8000")
}