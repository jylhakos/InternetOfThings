package database

import (
    "context"

    "log"

    "time"

    "fmt"

    "go.mongodb.org/mongo-driver/mongo"

    "go.mongodb.org/mongo-driver/mongo/options"

    getenv "web/utils/getenv"

)

func MongoDB() *mongo.Client {

    DB_URI := getenv.GetEnvVar("DB_URI")

    fmt.Println(DB_URI)

    client, err := mongo.NewClient(options.Client().ApplyURI(DB_URI))

    if err != nil {
        log.Fatal(err)
    }

    ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)

    err = client.Connect(ctx)

    if err != nil {
        log.Fatal(err)
    }

    return client
}

var Client *mongo.Client = MongoDB()

func Collection(client *mongo.Client, collectionName string) *mongo.Collection {

    var collection *mongo.Collection = client.Database("web").Collection(collectionName)

    return collection
}