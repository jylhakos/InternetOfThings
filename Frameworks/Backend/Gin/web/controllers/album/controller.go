package album

import (
    "context"

    "fmt"

    "log"

    "time"

    "github.com/gin-gonic/gin"

    "github.com/go-playground/validator/v10"

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

func AlbumsByArtist(c *gin.Context) ([]models.Album, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var albums []models.Album

    artist := c.Params.ByName("artist")

    fmt.Sprintf(artist)

    filter := bson.M{{"Artist": artist}}

    if err != nil {
        log.Fatal(err)
    }

    //cur, err := albumCollection.Find(context.Background(), filter)

    cur, err := albumCollection.Find(ctx, filter)

    defer cancel()

    if err != nil {
        log.Fatal(err)
    }

    for cur.Next(ctx) {

        var album bson.M

        e := cur.Decode(&album)

        if e != nil {
            log.Fatal(e)
        }

        albums = append(albums, album)
    }

    if err := cur.Err(); err != nil {
        log.Fatal(err)
        fmt.Errorf("AlbumsByArtist error", err)
    }

    cur.Close(c.Context())
    
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

func AlbumByID(c *gin.Context) (Album, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var album Album

    id := c.Params("id")

    filter := bson.D{{"ID": id}}

    err := albumCollection.FindOne(ctx, filter).Decode(album)

    defer cancel()

    if err != nil {

        log.Fatal(err)

        fmt.Errorf("AlbumByID error", err)
    }

    return album, nil
}

func AddAlbum(c *gin.Context) (int64, error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

	var lastInsertId int64

    var album Album

    if err := c.ShouldBindJSON(&album); err != nil {

    c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})

        return
    }

	/*

    sqlStatement := `INSERT INTO album (title, artist, price) VALUES ($1, $2, $3) RETURNING id;`

    err := db.QueryRow(sqlStatement, alb.Title, alb.Artist, alb.Price).Scan(&lastInsertId)

    */

    defer cancel()

    if err != nil {
        return 0, fmt.Errorf("addAlbum: %v", err)
    }

    //id, err := result.LastInsertId()

    if err != nil {
        return 0, fmt.Errorf("addAlbum: %v", err)
    }

    fmt.Sprintf("Added Album ", lastInsertId)

    return lastInsertId, nil
}

func UpdateAlbum(c *gin.Context) (error) {

    //var lastInsertId int64

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    var album Album

    if err := c.ShouldBindJSON(&album); err != nil {

    c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    fmt.Printf("Artist: %v Price: %f\n", album.Artist, album.Price)

    update := bson.M{"id":album.ID,"title": album.Title, "artist":album.Artist, "price":album.Price}

    result, err := albumCollection.UpdateOne(c, bson.M{"artist": album.Artist}, bson.M{"$set": update})
    
    defer cancel()

    if err != nil {
        c.JSON(http.StatusInternalServerError, responses.UserResponse{Status: http.StatusInternalServerError, Message: "Error", Data: map[string]interface{}{"data": err.Error()}})
        fmt.Errorf("UpdateAlbum error", err)
        return
    }

    /*

    sqlStatement := `UPDATE album SET price = $2 WHERE artist = $1;`

    result, err := db.Exec(sqlStatement, alb.Artist, alb.Price)

    */

    fmt.Printf("Updated: %v %v\n", result, err)

    rows, err := result.RowsAffected()

    fmt.Printf("RowsAffected: %v %v\n", rows, err)

    return nil
}

func DeleteAlbum(c *gin.Context) (error) {

    var ctx, cancel = context.WithTimeout(context.Background(), 100*time.Second)

    id := c.Params("id")

    filter := bson.D{{"ID": id}}

    /*

    result, err := db.Exec(sqlStatement, id)

    if err != nil {
        return fmt.Errorf("%v", err)
    }

    */

    defer cancel()

    fmt.Printf("Deleted: %v\n", result)

    return nil
}