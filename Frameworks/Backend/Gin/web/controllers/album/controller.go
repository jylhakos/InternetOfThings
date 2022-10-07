package album

import (
    "context"

    "fmt"

    "log"

    "time"

    "net/http"

    "github.com/gin-gonic/gin"

    //"github.com/go-playground/validator/v10"

    "go.mongodb.org/mongo-driver/bson"

    "go.mongodb.org/mongo-driver/bson/primitive"

    "go.mongodb.org/mongo-driver/mongo"

    database "web/database"
    
    models "web/models/album"
)

var albumCollection *mongo.Collection = database.Collection(database.Client, "album")

 
func FindAlbums() gin.HandlerFunc {

    return func(c *gin.Context) {

        fmt.Println("FindAlbums()")

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

        var albums []models.Album

        filter := bson.D{{}}

        cur, err := albumCollection.Find(ctx, filter)

        defer cancel()

        if err != nil {

            log.Fatal(err)

            c.JSON(http.StatusBadRequest, gin.H{"Error": err.Error()})

            return
        }

        for cur.Next(ctx) {

            var album models.Album

            e := cur.Decode(&album)

            if e != nil {
                log.Fatal(e)
            }

            fmt.Sprintf("%v %s %s %s", album.ID, album.Title, album.Artist, album.Price)

            albums = append(albums, album)

        }

        if err := cur.Err(); err != nil {

            log.Fatal(err)

            fmt.Errorf("GetAlbums error", err)

            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

            return
        }

        cur.Close(ctx)
        
        c.JSON(http.StatusOK, albums)
    }
}

func FindAlbumsByArtist() gin.HandlerFunc { 

    return func(c *gin.Context) {

        fmt.Println("FindAlbumsByArtist()")

        // Parsing data by query string parameters

        artist := c.Params.ByName("artist")

        fmt.Println("artist", artist)

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

        var results []models.Album

        // Parsing data from HTTP request body

        /*
        var album models.Album

        if err := c.BindJSON(&album); err != nil {

            fmt.Println("Error", err)

            c.JSON(http.StatusBadRequest, gin.H{"Error": err.Error()})

            defer cancel()
        }

        fmt.Println("album.Artist", album.Artist)
        */

        //filter := bson.M{"artist": bson.M{"$regex": artist}}

        filter := bson.M{"artist": bson.M{"$eq": artist}}

        fmt.Println("filter", filter)

        cursor, err := albumCollection.Find(ctx, filter)

        defer cancel()

        if err != nil {

            fmt.Println("Error", err)

            log.Fatal(err)

            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

            return
        }

        if err = cursor.All(ctx, &results); err != nil {

            fmt.Println("Error", err)

            log.Fatal(err)

            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

            return
        }

        for _, result := range results {
            fmt.Println(result)
        }

        c.JSON(http.StatusOK, results)

    	/*

        rows, err := db.Query("SELECT * FROM album WHERE artist = $1", name)

        if err != nil {

            return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
        }

        defer rows.Close()

        for rows.Next() {

            var alb Album

           if err := rows.Scan(&alb.ID, &alb.Title, &alb.Artist, &alb.Price); err != nil {
                return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
            }

            albums = append(albums, alb)
        }

        if err := rows.Err(); err != nil {
            return nil, fmt.Errorf("albumsByArtist %q: %v", name, err)
        }
        
        */
    }
}

func FindAlbumByID() gin.HandlerFunc { 

    return func(c *gin.Context) {

        fmt.Println("FindAlbumByID()")

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

        var album models.Album

        id := c.Params.ByName("id")

        fmt.Println("id", id)

        _id, _ := primitive.ObjectIDFromHex(id)

        fmt.Println("_id", _id)

        /*
        if err := c.BindJSON(&album); err != nil {

            fmt.Println(err)

            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

            return
        }

        filter := bson.M{"_id": album.ID}
        */

        filter := bson.M{"_id": _id}

        fmt.Println(filter)

        if error := albumCollection.FindOne(ctx, filter).Decode(&album); error != nil {
            fmt.Println("Error", error)
            c.JSON(http.StatusInternalServerError, gin.H{"error": error.Error()})
            return
        }

        defer cancel()

        c.JSON(http.StatusOK, album)
    }
}

func AddAlbum() gin.HandlerFunc { 

    return func(c *gin.Context) {

        fmt.Println("AddAlbum()")

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

        var album models.Album

        album.ID = primitive.NewObjectID()

        fmt.Println("album.ID", album.ID.String())

        if error := c.ShouldBindJSON(&album); error != nil {

            fmt.Println("album", album, "error", error)
            
            c.JSON(http.StatusBadRequest, gin.H{"Error": error.Error()})

            return
        }

        result, error := albumCollection.InsertOne(ctx, album)

        defer cancel()

        if error != nil {

            fmt.Errorf("addAlbum: %v", error)

            c.JSON(http.StatusInternalServerError, gin.H{"Error": error})

            return
        }

        fmt.Sprintf("result", result)
        
        //id := result.InsertedID.(primitive.ObjectID).String()

        //id, err := result.LastInsertId()

        fmt.Sprintf("Album", album)

        c.JSON(http.StatusOK, album)
    }
}

func UpdateAlbumByID() gin.HandlerFunc { 

    return func(c *gin.Context) {

        fmt.Println("UpdateAlbumByID()")

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

        var album models.Album

        if error := c.ShouldBindJSON(&album); error != nil {

            fmt.Println("error", error)

            c.JSON(http.StatusBadRequest, gin.H{"Error": error.Error()})

            return
        }

        fmt.Println("_id", album.ID)

        fmt.Printf("_id: %v, Artist: %s Title: %s Price: %s\n", album.ID, album.Artist, album.Title, album.Price)

        update := bson.M{"_id": album.ID, "title": album.Title, "artist":album.Artist, "price":album.Price}

        result, error := albumCollection.UpdateOne(ctx, bson.M{"_id": album.ID}, bson.M{"$set": update})

        //result, error := albumCollection.UpdateOne(ctx, bson.M{"artist": album.Artist}, bson.M{"$set": update})

        if error != nil {

            fmt.Errorf("Error", error)

            c.JSON(http.StatusInternalServerError, gin.H{"message": error})

            return
        }

        defer cancel()

        /*

        sqlStatement := `UPDATE album SET price = $2 WHERE artist = $1;`

        result, err := db.Exec(sqlStatement, alb.Artist, alb.Price)

        */

        fmt.Printf("Updated: %v\n", result)

        c.JSON(http.StatusOK, "OK")
    }
}

func DeleteAlbumByID() gin.HandlerFunc {

    return func(c *gin.Context) {

        fmt.Println("DeleteAlbumByID()")

        var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

        var album models.Album

        //id := c.Params("id")

        if error := c.ShouldBindJSON(&album); error != nil {

            fmt.Errorf("Error", error)

            c.JSON(http.StatusBadRequest, gin.H{"error": error.Error()})

            return
        }

        fmt.Println("_id", album.ID)

        filter := bson.M{"_id": album.ID}

        result, error := albumCollection.DeleteOne(ctx, filter) 

        if error != nil {

            fmt.Errorf("Error", error)
            
            c.JSON(http.StatusBadRequest, gin.H{"Error": error.Error()})

            return
        }

        defer cancel()

        fmt.Printf("Deleted: %v\n", result)

        c.JSON(http.StatusOK, "OK")
    }
}