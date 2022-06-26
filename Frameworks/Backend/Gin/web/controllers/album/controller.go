package album

import (
    "context"
    "fmt"
    "log"

    database "web/service/database"
    
    models "web/service/models"
)

var albumCollection *mongo.Collection = database.Collection(database.Client, "album")

func GetAlbums(c *gin.Context) {

    var albums []Album

    cur, err := albumCollection.Find(c.Context(), bson.D{{}})

    if err != nil {
        log.Fatal(err)
    }

    for cur.Next(c.Context()) {

        var album bson.M

        e := cur.Decode(&album)

        if e != nil {
            log.Fatal(e)
        }

        albums = append(albums, album)

    }

    if err := cur.Err(); err != nil {
        log.Fatal(err)
    }

    cur.Close(c.Context())
    
    return albums, nil
}

func AlbumsByArtist(c *gin.Context) ([]Album, error) {

    var albums []Album

    artist := c.Params("artist")

    filter := bson.D{{"Artist": artist}}

    //cur, err := albumCollection.Find(context.Background(), filter)

    cur, err := albumCollection.Find(c.Context(), filter)

    if err != nil {
        log.Fatal(err)
    }

    for cur.Next(c.Context()) {

        var album bson.M

        e := cur.Decode(&album)

        if e != nil {
            log.Fatal(e)
        }

        albums = append(albums, album)
    }

    if err := cur.Err(); err != nil {
        log.Fatal(err)
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

    var album Album

    id := c.Params("id")

    filter := bson.D{{"ID": id}}

    err := albumCollection.FindOne(c.Context(), filter).Decode(album)

    if err != nil {

        log.Fatal(err)
    }

    return album, nil
}

func AddAlbum(c *gin.Context) (int64, error) {

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

    if err != nil {
        return 0, fmt.Errorf("addAlbum: %v", err)
    }

    //id, err := result.LastInsertId()

    if err != nil {
        return 0, fmt.Errorf("addAlbum: %v", err)
    }

    return lastInsertId, nil
}

func UpdateAlbum(c *gin.Context) (error) {

    fmt.Printf("Artist: %v Price: %f\n", alb.Artist, alb.Price)

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

    id := c.Params("id")

    filter := bson.D{{"ID": id}}

    /*

    result, err := db.Exec(sqlStatement, id)

    if err != nil {
        return fmt.Errorf("%v", err)
    }

    */

    fmt.Printf("Deleted: %v\n", result)

    return nil
}