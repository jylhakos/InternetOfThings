package middleware

import (
    "fmt"
    "net/http"
    
    "github.com/gin-gonic/gin"

    helper "web/service/utils/tokenizer"

)

func Authorization() gin.HandlerFunc {

    return func(c *gin.Context) {

        clientToken := c.Request.Header.Get("Authorization")

        if clientToken == "" {

            c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("No Authorization Header")})
            
            c.Abort()
            
            return
        }

        claims, err := helper.ValidateToken(clientToken)

        if err != "" {

            c.JSON(http.StatusInternalServerError, gin.H{"error": err})

            c.Abort()

            return
        }

        c.Set("email", claims.Email)

        c.Set("name", claims.Name)

        c.Set("uid", claims.Uid)

        c.Next()
    }
}
