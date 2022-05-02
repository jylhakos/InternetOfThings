package main

import (
 "database/sql"
 "fmt"
 "log"
 "errors"
 _ "github.com/lib/pq"
)

func checkError(err error) {
	if err != nil {
		panic(err)
	}
}

var db *sql.DB

type Album struct {
    ID     int64
    Title  string
    Artist string
    Price  float32
}

func main() {

	const (
		host = "localhost"
		port = 5432
		user = "postgres"
		password = "postgres"
		database = "recordings"
	)

	pg_conn := fmt.Sprintf("port=%d host=%s user=%s password=%s dbname=%s sslmode=disable", port, host, user, password, database)

	err := errors.New("")

	db, err = sql.Open("postgres", pg_conn)

	checkError(err)

	err = db.Ping()

	checkError(err)

	fmt.Println("Connected to database")

	albums, err := albumsByArtist("John Coltrane")

    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Albums found: %v\n", albums)

    albID, err := addAlbum(Album{
    	Title:  "The Modern Sound of Betty Carter",
    	Artist: "Betty Carter",
    	Price:  49.99,
	})

	if err != nil {
    	log.Fatal(err)
	}

	fmt.Printf("ID of added album: %v\n", albID)

	alb, err := albumByID(2)

    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Album found: %v\n", alb)

}

func albumsByArtist(name string) ([]Album, error) {
    
	var albums []Album

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

    return albums, nil

}

func albumByID(id int64) (Album, error) {

    var alb Album

    row := db.QueryRow("SELECT * FROM album WHERE id = $1", id)
    
    if err := row.Scan(&alb.ID, &alb.Title, &alb.Artist, &alb.Price); err != nil {
        
        if err == sql.ErrNoRows {

            return alb, fmt.Errorf("albumsById %d: no such album", id)
        }

        return alb, fmt.Errorf("albumsById %d: %v", id, err)
    }

    return alb, nil
}

func addAlbum(alb Album) (int64, error) {

	var lastInsertId int64

	sqlStatement := `INSERT INTO album (title, artist, price) VALUES ($1, $2, $3) RETURNING id`

    err := db.QueryRow(sqlStatement, alb.Title, alb.Artist, alb.Price).Scan(&lastInsertId)

    if err != nil {
        return 0, fmt.Errorf("addAlbum: %v", err)
    }

    //id, err := result.LastInsertId()

    if err != nil {
        return 0, fmt.Errorf("addAlbum: %v", err)
    }

    return lastInsertId, nil
}