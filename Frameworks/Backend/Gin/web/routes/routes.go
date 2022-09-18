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

    routes.GET("/albums", albumController.GetAlbums())

    routes.GET("/albums/:artist", albumController.AlbumsByArtist())

    routes.GET("/albums/:artist/:id", albumController.AlbumByID())

    routes.POST("/albums", albumController.AddAlbum())

    routes.PUT("/albums", albumController.UpdateAlbum())

    routes.DELETE("/albums/:id", albumController.DeleteAlbum())
}