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

    routes.GET("/albums:artist", albumController.AlbumsByArtist(string))

    routes.GET("/albums:id", albumController.AlbumByID(int64))

    routes.POST("/albums", albumController.AddAlbum(Album))

    routes.PUT("/albums", albumController.UpdateAlbum(Album))

    routes.DELETE("/albums:id", albumController.DeleteAlbum(int64))
}