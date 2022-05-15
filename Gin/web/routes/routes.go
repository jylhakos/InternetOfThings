package routes

import (
    "github.com/gin-gonic/gin"

    controller "web/service/controllers"
)

func UserRoutes(incomingRoutes *gin.Engine) {

    incomingRoutes.POST("/users/signup", controller.SignUp())

    incomingRoutes.POST("/users/login", controller.Login())
}