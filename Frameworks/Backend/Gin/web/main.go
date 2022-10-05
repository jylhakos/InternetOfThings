package main

import (
    "github.com/gin-gonic/gin"

    "github.com/gin-contrib/cors"

    _ "github.com/heroku/x/hmetrics/onload"

    "errors"

    "fmt"

    getenv "web/utils/getenv"

    //middleware "web/middleware/authorization"

    routes "web/routes"
)

func Test() error {

    return errors.New("No Errors")

    // return fmt.Errorf("Error")

    // return nil
}

func main() {

    port := getenv.GetEnvVar("PORT")

    if port == "" {
        port = "8001"
    }

    router := gin.New()

    router.Use(cors.New(cors.Config {
        AllowOrigins:     []string{"http://localhost:19006"},
        AllowMethods:     []string{"GET","POST","OPTIONS"},
        AllowHeaders:     []string{"Content-Type","Content-Length","Authorization"},
        AllowCredentials: true,
        //AllowOriginFunc: func(origin string) bool {
        //  return origin == "https://localhost"
        //},
    }))

    router.Use(gin.Logger())

    router.GET("/api", func(c *gin.Context) {
        c.JSON(200, gin.H{"success": "Access granted for /api"})
    })

    routes.UserRoutes(router)

    //router.Use(middleware.Authorization())

    routes.AlbumRoutes(router)

    err := Test()

    fmt.Println(err)

    router.Run(":" + port)
}