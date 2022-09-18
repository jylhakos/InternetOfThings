package database

import (
    "context"

    "log"

    "time"

    "fmt"

    "go.mongodb.org/mongo-driver/mongo"

    "go.mongodb.org/mongo-driver/mongo/options"

    "go.mongodb.org/mongo-driver/bson"

    "go.mongodb.org/mongo-driver/mongo/readpref"

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

        fmt.Println(err)

        log.Fatal(err)
    }

    err = client.Ping(ctx, readpref.Primary())

    if err != nil {

        fmt.Println(err)

        log.Fatal(err)
    }   

    databases, err := client.ListDatabaseNames(ctx, bson.M{})

    if err != nil {

        fmt.Println(err)

        log.Fatal(err)
    }

    fmt.Println(databases)

    return client
}

var Client *mongo.Client = MongoDB()

func Collection(client *mongo.Client, collectionName string) *mongo.Collection {

    var collection *mongo.Collection = client.Database("web").Collection(collectionName)

    return collection
}