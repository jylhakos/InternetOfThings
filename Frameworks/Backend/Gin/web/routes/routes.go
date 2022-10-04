package routes

import (
    "github.com/gin-gonic/gin"

    userController "web/controllers/user"
    
    albumController "web/controllers/album"

)

func UserRoutes(routes *gin.Engine) {

    routes.POST("/users/signup", userController.SignUp())

    routes.POST("/users/login", userController.Login())
}

func AlbumRoutes(routes *gin.Engine) {

    routes.GET("/albums", albumController.FindAlbums())

    routes.GET("/albums/:artist", albumController.FindAlbumsByArtist())

    routes.GET("/album/:id", albumController.FindAlbumByID())

    routes.POST("/albums", albumController.AddAlbum())

    routes.PUT("/album/:id", albumController.UpdateAlbumByID())

    routes.DELETE("/album/:id", albumController.DeleteAlbumByID())
}