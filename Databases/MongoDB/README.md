# Non-Sql Database

## MongoDB

You can start the mongod process by issuing systemctl start command.

```

$ sudo systemctl start mongod

```

### A struct object

In order to get the MongoDB data returned by the API call, it’s important to first declare a struct object.

Create a struct object in the Golang script for the MongoDB fields returned by API call.

```

type Album struct {
    ID     string  `json:"id"`
    Title  string  `json:"title"`
    Artist string  `json:"artist"`
    Price  float64 `json:"price"`
}


```

### Golang’s Context

We can use the options.Client() method and have it return a options.ClientOptions object.

We declare context instance which can assist managing timeouts for the MongoDB API requests.

```

web/database/database.go

import (
    "context"
    "time"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

func MongoDB() *mongo.Client {

	client, err := mongo.NewClient(options.Client().ApplyURI("mongodb://127.0.0.1:27017/web?authSource=admin"))

	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)

    err = client.Connect(ctx)

    return client
}

```
### Connect to MongoDB

Declare a collection instance using the client instance of the mongo-driver package.

```

var Client *mongo.Client = MongoDB()

func Collection(client *mongo.Client, collectionName string) *mongo.Collection {

    var collection *mongo.Collection = client.Database("web").Collection(collectionName)

    return collection
}

```

### Make API calls to the MongoDB

We use the var statement to declare an instance of the Album struct. 

We call the collection instance’s FindOne() function to get a document from MongoDB.

```

web/controllers/album/controller.go

func AlbumsByArtist(name string) ([]Album, error) {
    
	var albums []Album


```

### Find documents

The bson.D{{}} specifies all documents

```

filter := bson.D{{}}

```

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Databases/MongoDB/mongodb.png?raw=true)


## References

MongoDB https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/