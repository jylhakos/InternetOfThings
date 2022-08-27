package tokenizer

import (
    "context"

    "fmt"

    "log"
    
    "time"

    jwt "github.com/golang-jwt/jwt"
    
    "go.mongodb.org/mongo-driver/bson"

    "go.mongodb.org/mongo-driver/bson/primitive"

    "go.mongodb.org/mongo-driver/mongo"

    "go.mongodb.org/mongo-driver/mongo/options"

    getenv "web/utils/getenv"

    database "web/database"
)

type SignedDetails struct {
    Uid     string
    Email   string
    Name    string
    jwt.StandardClaims
}

var userCollection *mongo.Collection = database.Collection(database.Client, "user")

var SECRET_KEY string = getenv.GetEnvVar("SECRET_KEY")

func GenerateAllTokens(uid string, email string, name string) (signedToken string, signedRefreshToken string, err error) {

    claims := &SignedDetails{
        Uid:        uid,
        Email:      email,
        Name: name,
        StandardClaims: jwt.StandardClaims{
            ExpiresAt: time.Now().Local().Add(time.Hour * time.Duration(24)).Unix(),
        },
    }

    refreshClaims := &SignedDetails{

        StandardClaims: jwt.StandardClaims{

            ExpiresAt: time.Now().Local().Add(time.Hour * time.Duration(168)).Unix(),
        },
    }

    token, err := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(SECRET_KEY))
    
    refreshToken, err := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims).SignedString([]byte(SECRET_KEY))

    if err != nil {

        log.Panic(err)

        return
    }

    return token, refreshToken, err
}

func ValidateToken(signedToken string) (claims *SignedDetails, msg string) {

    token, err := jwt.ParseWithClaims(
        signedToken,
        &SignedDetails{},
        func(token *jwt.Token) (interface{}, error) {

            return []byte(SECRET_KEY), nil
        },
    )

    if err != nil {

        msg = err.Error()

        return
    }

    claims, ok := token.Claims.(*SignedDetails)

    if !ok {

        msg = fmt.Sprintf("The token is not valid.")

        msg = err.Error()

        return
    }

    if claims.ExpiresAt < time.Now().Local().Unix() {

        msg = fmt.Sprintf("The token is expired.")

        msg = err.Error()

        return
    }

    return claims, msg
}

func UpdateAllTokens(signedToken string, signedRefreshToken string, userId string) {
    
    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var updateObj primitive.D

    updateObj = append(updateObj, bson.E{"token", signedToken})
    
    updateObj = append(updateObj, bson.E{"refresh_token", signedRefreshToken})

    Updated_at, _ := time.Parse(time.RFC3339, time.Now().Format(time.RFC3339))
    
    updateObj = append(updateObj, bson.E{"updated_at", Updated_at})

    upsert := true

    filter := bson.M{"user_id": userId}

    opt := options.UpdateOptions{
        Upsert: &upsert,
    }

    _, err := userCollection.UpdateOne(
        ctx,
        filter,
        bson.D{
            {"$set", updateObj},
        },
        &opt,
    )
    
    defer cancel()

    if err != nil {
        log.Panic(err)
        return
    }

    return
}