package routes

import (
    "github.com/gin-gonic/gin"

    controller "web/service/controllers/user"
)

func UserRoutes(userRoutes *gin.Engine) {

    userRoutes.POST("/users/signup", controller.SignUp())

    userRoutes.POST("/users/login", controller.Login())
}