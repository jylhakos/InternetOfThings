package main

import (
    "github.com/gin-gonic/gin"

    _ "github.com/heroku/x/hmetrics/onload"

    getenv "web/service/utils/getenv"

    middleware "web/service/middleware"

    routes "web/service/routes"
)

func main() {

    port := getenv.GetEnvVar("PORT")

    if port == "" {
        port = "8001"
    }

    router := gin.New()

    router.Use(gin.Logger())

    routes.Routes(router)

    router.Use(middleware.Authorization())

    router.GET("/api", func(c *gin.Context) {

        c.JSON(200, gin.H{"success": "Access granted for /api"})

    })

    router.Run(":" + port)
}