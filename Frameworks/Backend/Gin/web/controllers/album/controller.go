package album

func AlbumsByArtist(name string) ([]Album, error) {
    
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

func AlbumByID(id int64) (Album, error) {

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

func AddAlbum(alb Album) (int64, error) {

	var lastInsertId int64

	sqlStatement := `INSERT INTO album (title, artist, price) VALUES ($1, $2, $3) RETURNING id;`

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

func UpdateAlbum(alb Album) (error) {

    fmt.Printf("Artist: %v Price: %f\n", alb.Artist, alb.Price)

    sqlStatement := `UPDATE album SET price = $2 WHERE artist = $1;`

    result, err := db.Exec(sqlStatement, alb.Artist, alb.Price)

    fmt.Printf("Updated: %v %v\n", result, err)

    rows, err := result.RowsAffected()

    fmt.Printf("RowsAffected: %v %v\n", rows, err)

    return nil
}

func DeleteAlbum(id int64) (error) {

    sqlStatement := `DELETE FROM album WHERE id = $1;`

    result, err := db.Exec(sqlStatement, id)

    if err != nil {
        return fmt.Errorf("%v", err)
    }

    fmt.Printf("Deleted: %v\n", result)

    return nil
}