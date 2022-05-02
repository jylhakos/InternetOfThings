# PostgreSQL by Golang

This page introduces accessing a relational database with Golang and the database/sql package library.

The database/sql package includes types and functions for connecting to databases, executing transactions, canceling an operation in progress, and more functions.

## Prerequisites

[ ] An installation of the PostgreSQL relational database management system (DBMS).

[ ] An installation of Golang.

### Create a folder for your code

Create a directory for your code.

```

$ mkdir <FOLDER>

$ cd <FOLDER>

```

The below command creates go.mod file in which can track your code dependencies.

```

$ go mod init <PREFIX>/<FOLDER>

```

The <PREFIX> is a string that describes the location of module

Run the go mod init command, giving it your new code’s module path.

```

$ go mod init example/data-access

```

### Set up a database

At the command line, log into your DBMS.

```

$ sudo -i -u postgres psql

```

At the PostgreSQL command prompt, create a database.

```

postgres=# CREATE DATABASE recordings;

```

Switch connection to the created database.

```

postgres=# \c recordings;

```

Create an album table with four columns: title, artist, and price. 

```

postgres=# CREATE TABLE album (
			  id         SERIAL PRIMARY KEY,
			  title      VARCHAR(128) NOT NULL,
			  artist     VARCHAR(255) NOT NULL,
			  price      DECIMAL(5,2) NOT NULL
			);

```

Add rows onto the table with values.

```

postgres=# INSERT INTO album
  			(title, artist, price)
  			VALUES
			  ('Blue Train', 'John Coltrane', 56.99),
			  ('Giant Steps', 'John Coltrane', 63.99),
			  ('Jeru', 'Gerry Mulligan', 17.99),
			  ('Sarah Vaughan', 'Sarah Vaughan', 34.98);

```

### Find and import a database driver

In your browser, visit the [SQLDrivers wiki page](https://github.com/golang/go/wiki/SQLDrivers) to identify a driver you can use.

Create main.go file in which to write your Golang code and paste the following code to import the driver package.

```

package main

import (
 "database/sql"
 _ "github.com/lib/pq"
)

```

### Get a database handle and connect

Declare a pointer of type ```*sql.DB```, which represents access to a specific database.

``` 

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

```

### Get the code

Use the go get command to add the github.com/lib/pq module as a dependency for your own module.

```

$ go get .

```

### Query for multiple rows

You’ll use DB.Query to execute a SELECT statement to query for albums table to return multiple rows.

```

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

```
### Query for a single row

You’ll use DB.QueryRow to execute a SELECT statement to query for a single row in the database.

```

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

```

### Add new data

You’ll use Go to execute an SQL INSERT statement to add a new row to the database.

```

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

```

### Run the code

Run the code by typing go run command.

```

$ go run .

```

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Database/database.png?raw=true)