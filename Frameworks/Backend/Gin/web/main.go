package main

import (
    "github.com/gin-gonic/gin"

    _ "github.com/heroku/x/hmetrics/onload"

    getenv "web/utils/getenv"

    middleware "web/middleware/authorization"

    routes "web/routes"
)

func main() {

    port := getenv.GetEnvVar("PORT")

    if port == "" {
        port = "8001"
    }

    router := gin.New()

    router.Use(gin.Logger())

    router.GET("/api", func(c *gin.Context) {

        c.JSON(200, gin.H{"success": "Access granted for /api"})

    })

    routes.UserRoutes(router)

    router.Use(middleware.Authorization())

    routes.AlbumRoutes(router)

    router.Run(":" + port)
}