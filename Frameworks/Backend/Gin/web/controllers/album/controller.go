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

func GetAlbums(c *gin.Context) ([]models.Album, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var albums []models.Album

    filter := bson.D{{}}

    cur, err := albumCollection.Find(ctx, filter)

    defer cancel()

    if err != nil {
        log.Fatal(err)
    }

    for cur.Next(ctx) {

        var album models.Album

        e := cur.Decode(&album)

        if e != nil {
            log.Fatal(e)
        }

        fmt.Sprintf(album.ID, album.Title, album.Artist, album.Price)

        albums = append(albums, album)

    }

    if err := cur.Err(); err != nil {
        log.Fatal(err)
        fmt.Errorf("GetAlbums error", err)
    }

    cur.Close(ctx)
    
    return albums, nil
}

func AlbumsByArtist(c *gin.Context) ([]bson.M, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    //var albums []models.Album
    var albums []bson.M

    //artist := c.Params.ByName("artist")

    //fmt.Sprintf(artist)

    var album models.Album

    if err := c.BindJSON(&album); err != nil {

        fmt.Println(err)

        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
     
        return nil, err
    }

    fmt.Println(album)

    filter := bson.M{"artist": album.Artist}

    fmt.Println(filter)

    //cur, err := albumCollection.Find(context.Background(), filter)

    cur, err := albumCollection.Find(ctx, filter)

    defer cancel()

    if err != nil {

        fmt.Println(err)

        log.Fatal(err)
    }

    for cur.Next(ctx) {

        var album bson.M

        e := cur.Decode(&album)

        if e != nil {
            log.Fatal(e)
        }

        fmt.Println(album)

        albums = append(albums, album)
    }

    if err := cur.Err(); err != nil {

        log.Fatal(err)

        fmt.Errorf("AlbumsByArtist error", err)
    }

    cur.Close(ctx)
    
    fmt.Println(albums)

    return albums, nil

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

func AlbumByID(c *gin.Context) (models.Album, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var album models.Album

    //id := c.Params("id")

    if err := c.BindJSON(&album); err != nil {

        fmt.Println(err)

        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
     
        return album, err
    }

    filter := bson.M{"id": album.ID}

    fmt.Println(filter)

    err := albumCollection.FindOne(ctx, filter).Decode(&album)

    defer cancel()

    if err != nil {

        log.Fatal(err)

        fmt.Errorf("AlbumByID error", err)
    }

    return album, nil
}

func AddAlbum(c *gin.Context) (string, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var album models.Album

    if err := c.ShouldBindJSON(&album); err != nil {

        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

        return "-1", err
    }

    result, err := albumCollection.InsertOne(ctx, album)

    defer cancel()

	/*

    sqlStatement := `INSERT INTO album (title, artist, price) VALUES ($1, $2, $3) RETURNING id;`

    err := db.QueryRow(sqlStatement, alb.Title, alb.Artist, alb.Price).Scan(&lastInsertId)

    */

    if err != nil {

        fmt.Errorf("addAlbum: %v", err)

        c.JSON(http.StatusInternalServerError, gin.H{"message": err})

        return "-1", err
    }

    id := result.InsertedID.(primitive.ObjectID).String()

    //id, err := result.LastInsertId()

    fmt.Sprintf("Album objectId", id)

    return id, nil
}

func UpdateAlbum(c *gin.Context) (error) {

    //var lastInsertId int64

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var album models.Album

    if err := c.ShouldBindJSON(&album); err != nil {

        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

        return err
    }

    fmt.Printf("Artist: %v Price: %f\n", album.Artist, album.Price)

    update := bson.M{"id":album.ID,"title": album.Title, "artist":album.Artist, "price":album.Price}

    result, err := albumCollection.UpdateOne(ctx, bson.M{"artist": album.Artist}, bson.M{"$set": update})
    
    defer cancel()

    if err != nil {

        c.JSON(http.StatusInternalServerError, gin.H{"message": err})

        fmt.Errorf("UpdateAlbum error", err)

        return err
    }

    /*

    sqlStatement := `UPDATE album SET price = $2 WHERE artist = $1;`

    result, err := db.Exec(sqlStatement, alb.Artist, alb.Price)

    */

    fmt.Printf("Updated: %v %v\n", result, err)

    return nil
}

func DeleteAlbum(c *gin.Context) (error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var album models.Album

    //id := c.Params("id")

    if err := c.ShouldBindJSON(&album); err != nil {

        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        
        return err
    }

    filter := bson.M{"id": album.ID}

    /*

    result, err := db.Exec(sqlStatement, id)

    if err != nil {
        return fmt.Errorf("%v", err)
    }

    */

    result, err := albumCollection.DeleteOne(ctx, filter) 

    defer cancel()

    if err != nil {
        return fmt.Errorf("%v", err)
    }

    fmt.Printf("Deleted: %v\n", result)

    return nil
}