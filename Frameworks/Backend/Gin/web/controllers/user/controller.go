package user

import (
    "context"

    "fmt"

    "log"

    "time"

    "net/http"

    "github.com/gin-gonic/gin"

    "github.com/go-playground/validator/v10"

    "go.mongodb.org/mongo-driver/bson"

    "go.mongodb.org/mongo-driver/bson/primitive"

    "go.mongodb.org/mongo-driver/mongo"

    "golang.org/x/crypto/bcrypt"

    database "web/database"
    
    models "web/models/user"

    helper "web/utils/tokenizer"
    
)

var userCollection *mongo.Collection = database.Collection(database.Client, "user")

var validate = validator.New()

func HashPassword(password string) string {

    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)

    if err != nil {

        log.Panic(err)
    }

    return string(bytes)
}

func VerifyPassword(userPassword string, providedPassword string) (bool, string) {
    
    err := bcrypt.CompareHashAndPassword([]byte(providedPassword), []byte(userPassword))
    
    check := true
    
    msg := ""

    if err != nil {

        msg = fmt.Sprintf("login or passowrd is incorrect")

        fmt.Errorf("login or passowrd is incorrect", providedPassword, userPassword)
        
        check = false
    }

    return check, msg
}

func SignUp() gin.HandlerFunc {

    return func(c *gin.Context) {

        fmt.Println("SignUp()")

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)
        
        var user models.User

        if err := c.BindJSON(&user); err != nil {

            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            
            return
        }

        validationErr := validate.Struct(user)

        if validationErr != nil {

            c.JSON(http.StatusBadRequest, gin.H{"error": validationErr.Error()})
            
            return
        }

        count, err := userCollection.CountDocuments(ctx, bson.M{"email": user.Email})
        
        defer cancel()
        
        if err != nil {

            log.Panic(err)

            c.JSON(http.StatusInternalServerError, gin.H{"error": "error occured while checking for the email"})
            
            return
        }

        password := HashPassword(*user.Password)

        user.Password = &password

        defer cancel()

        if count > 0 {

            c.JSON(http.StatusInternalServerError, gin.H{"error": "E-mail already exists."})
            
            return
        }

        user.Created_at, _ = time.Parse(time.RFC3339, time.Now().Format(time.RFC3339))
        
        user.Updated_at, _ = time.Parse(time.RFC3339, time.Now().Format(time.RFC3339))
        
        user.ID = primitive.NewObjectID()
        
        user.User_id = user.ID.Hex()
        
        token, refreshToken, _ := helper.GenerateAllTokens(*user.Email, *user.Name, user.User_id)
        
        user.Token = &token
        
        user.Refresh_token = &refreshToken

        resultInsertionNumber, insertErr := userCollection.InsertOne(ctx, user)
        
        if insertErr != nil {

            msg := fmt.Sprintf("User was not created", insertErr)
            
            c.JSON(http.StatusInternalServerError, gin.H{"error": msg})
            
            return
        }

        defer cancel()

        c.JSON(http.StatusOK, resultInsertionNumber)

    }
}

func Login() gin.HandlerFunc {

    return func(c *gin.Context) {

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)
        
        var user models.User
        
        var foundUser models.User

        if err := c.BindJSON(&user); err != nil {

            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

            fmt.Errorf("Login error", err)
            
            return
        }

        err := userCollection.FindOne(ctx, bson.M{"email": user.Email}).Decode(&foundUser)
        
        defer cancel()

        if err != nil {

            c.JSON(http.StatusInternalServerError, gin.H{"error": "E-mail is not found from MongoDB."})
            
            fmt.Errorf("E-mail is not found from MongoDB.", err)

            return
        }

        passwordIsValid, msg := VerifyPassword(*user.Password, *foundUser.Password)
        
        defer cancel()
        
        if passwordIsValid != true {

            c.JSON(http.StatusInternalServerError, gin.H{"error": msg})

            fmt.Errorf("Password is incorrect.")
            
            return
        }

        token, refreshToken, _ := helper.GenerateAllTokens(*foundUser.Email, *foundUser.Name, foundUser.User_id)

        helper.UpdateAllTokens(token, refreshToken, foundUser.User_id)

        fmt.Sprintf("The token has value ", token)

        c.JSON(http.StatusOK, foundUser)
    }
}