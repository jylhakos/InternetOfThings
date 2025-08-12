# Databases for Internet of Things (IoT)

*This documentation is part of the Internet of Things (IoT) project demonstrating database integration patterns for IoT applications.*

## Folders/Files

```
Databases/
├── MongoDB/          # NoSQL Document Database
│   ├── README.md     # MongoDB implementation guides
│   └── examples/     # Code examples and use cases
├── PostgreSQL/       # Relational Database
│   ├── README.md     # PostgreSQL with Go implementation
│   ├── main.go       # Go application example
│   ├── go.mod        # Go module definition
│   ├── go.sum        # Go dependencies
│   └── database.png  # Database diagram
├── Redis/            # In-Memory Cache Database
│   ├── README.md     # Redis memory caching guide
│   └── examples/     # Caching implementation examples
└── README.md         # This comprehensive overview
```

## Databases

### 🍃 MongoDB - NoSQL Document Database
MongoDB is a document-oriented NoSQL database designed for modern applications that require flexible schemas and horizontal scalability. Perfect for IoT applications handling diverse data formats.

**Features:**
- Document-based storage (JSON-like BSON format)
- Horizontal scaling with sharding
- Rich query language
- Flexible schema design
- Built-in replication

### 🐘 PostgreSQL - Relational Database
PostgreSQL is an open-source object-relational database system with strong ACID compliance and extensive SQL features. Ideal for IoT applications requiring complex queries and data integrity.

**Features:**
- ACID compliance
- SQL features
- JSON and JSONB support
- Full-text search
- Extensible with custom functions
- Strong consistency

### ⚡ Redis - In-Memory Data Store
Redis is an in-memory data structure store used as a database, cache, and message broker. Essential for IoT applications requiring real-time data processing and caching.

**Features:**
- In-memory storage for ultra-fast access
- Multiple data structures (strings, hashes, lists, sets)
- Pub/Sub messaging
- Persistence options
- Clustering support
- Lua scripting

## Programming Language Integration

### 🔧 CRUD Operations with RESTful APIs

#### Go Language Integration

**PostgreSQL with Go:**
```go
// Using database/sql and pq driver
import (
    "database/sql"
    _ "github.com/lib/pq"
    "github.com/gorilla/mux"
)

// CRUD operations example
func CreateUser(w http.ResponseWriter, r *http.Request) {
    // INSERT operation
}

func GetUsers(w http.ResponseWriter, r *http.Request) {
    // SELECT operation
}

func UpdateUser(w http.ResponseWriter, r *http.Request) {
    // UPDATE operation
}

func DeleteUser(w http.ResponseWriter, r *http.Request) {
    // DELETE operation
}
```

**MongoDB with Go:**
```go
// Using mongo-driver
import (
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

// CRUD operations with MongoDB
func CreateDocument(collection *mongo.Collection, doc interface{}) {
    // Insert document
}
```

**Redis with Go:**
```go
// Using go-redis
import "github.com/go-redis/redis/v8"

func CacheData(rdb *redis.Client, key string, value interface{}) {
    // SET operation
}
```

#### Python Integration

**PostgreSQL with Python:**
```python
# Using psycopg2
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user():
    # INSERT operation
    pass

@app.route('/users', methods=['GET'])
def get_users():
    # SELECT operation
    pass

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # UPDATE operation
    pass

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # DELETE operation
    pass
```

**MongoDB with Python:**
```python
# Using pymongo
from pymongo import MongoClient
from flask import Flask

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')

@app.route('/documents', methods=['POST'])
def create_document():
    # Insert document
    pass
```

**Redis with Python:**
```python
# Using redis-py
import redis
from flask import Flask

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/cache/<key>')
def get_cached_data(key):
    # GET from cache
    return r.get(key)
```

#### Java Integration

**PostgreSQL with Java:**
```java
// Using JDBC and Spring Boot
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserRepository userRepository;
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        // CREATE operation
        return ResponseEntity.ok(userRepository.save(user));
    }
    
    @GetMapping
    public List<User> getAllUsers() {
        // READ operation
        return userRepository.findAll();
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
        // UPDATE operation
        return ResponseEntity.ok(userRepository.save(user));
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        // DELETE operation
        userRepository.deleteById(id);
        return ResponseEntity.ok().build();
    }
}
```

**MongoDB with Java:**
```java
// Using MongoDB Java Driver
@RestController
@RequestMapping("/api/documents")
public class DocumentController {
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    @PostMapping
    public Document createDocument(@RequestBody Document document) {
        return mongoTemplate.save(document);
    }
}
```

#### JavaScript/Node.js Integration

**PostgreSQL with Node.js:**
```javascript
// Using pg (node-postgres)
const express = require('express');
const { Pool } = require('pg');

const app = express();
const pool = new Pool({
    connectionString: 'postgresql://username:password@localhost:5432/database'
});

// CRUD operations
app.post('/users', async (req, res) => {
    // CREATE operation
    const { name, email } = req.body;
    const result = await pool.query('INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *', [name, email]);
    res.json(result.rows[0]);
});

app.get('/users', async (req, res) => {
    // READ operation
    const result = await pool.query('SELECT * FROM users');
    res.json(result.rows);
});

app.put('/users/:id', async (req, res) => {
    // UPDATE operation
    const { id } = req.params;
    const { name, email } = req.body;
    const result = await pool.query('UPDATE users SET name = $1, email = $2 WHERE id = $3 RETURNING *', [name, email, id]);
    res.json(result.rows[0]);
});

app.delete('/users/:id', async (req, res) => {
    // DELETE operation
    const { id } = req.params;
    await pool.query('DELETE FROM users WHERE id = $1', [id]);
    res.json({ message: 'User deleted successfully' });
});
```

**MongoDB with Node.js:**
```javascript
// Using MongoDB Node.js driver
const express = require('express');
const { MongoClient } = require('mongodb');

const app = express();
const client = new MongoClient('mongodb://localhost:27017');

app.post('/documents', async (req, res) => {
    const db = client.db('mydb');
    const collection = db.collection('documents');
    const result = await collection.insertOne(req.body);
    res.json(result);
});

app.get('/documents', async (req, res) => {
    const db = client.db('mydb');
    const collection = db.collection('documents');
    const documents = await collection.find({}).toArray();
    res.json(documents);
});
```

**Redis with Node.js:**
```javascript
// Using ioredis
const express = require('express');
const Redis = require('ioredis');

const app = express();
const redis = new Redis();

app.get('/cache/:key', async (req, res) => {
    const { key } = req.params;
    const value = await redis.get(key);
    res.json({ key, value });
});

app.post('/cache', async (req, res) => {
    const { key, value, ttl } = req.body;
    await redis.setex(key, ttl || 3600, value);
    res.json({ message: 'Cached successfully' });
});
```

## AWS Integration

### MongoDB and AWS

**MongoDB Atlas on AWS:**
- Fully-managed cloud database service on AWS infrastructure
- Automatic scaling, backup, and monitoring
- Integration with AWS services (Lambda, EC2, S3)

**Amazon DocumentDB:**
- AWS-managed MongoDB-compatible database service
- Compatible with MongoDB APIs and tools
- Built-in security and compliance features

**AWS Integration Example (Go):**
```go
// Connecting to MongoDB Atlas
import (
    "context"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

func ConnectToAtlas() (*mongo.Client, error) {
    uri := "mongodb+srv://<username>:<password>@cluster.mongodb.net/"
    client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(uri))
    return client, err
}
```

### PostgreSQL and AWS

**Amazon RDS for PostgreSQL:**
- Fully managed PostgreSQL database service
- Automated backups, patching, and scaling
- High availability with Multi-AZ deployments

**Amazon Aurora PostgreSQL:**
- High-performance, cloud-native PostgreSQL-compatible database
- Up to 3x faster performance than standard PostgreSQL
- Automatic failover and continuous backup

**AWS Integration Examples:**

**Python with RDS:**
```python
# Using AWS Advanced Python Wrapper Driver
import aws_advanced_python_wrapper.pg8000_driver as aws_pg8000
import boto3

# Connection with IAM authentication
def connect_with_iam():
    client = boto3.client('rds')
    token = client.generate_db_auth_token(
        DBHostname='mypostgres.cluster-xyz.us-east-1.rds.amazonaws.com',
        Port=5432,
        DBUsername='myuser'
    )
    
    conn = aws_pg8000.connect(
        host='mypostgres.cluster-xyz.us-east-1.rds.amazonaws.com',
        user='myuser',
        password=token,
        database='mydb'
    )
    return conn
```

**Go with Aurora:**
```go
// Using AWS SDK for Go
import (
    "database/sql"
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/rds"
    _ "github.com/lib/pq"
)

func ConnectWithIAM() (*sql.DB, error) {
    sess := session.Must(session.NewSession())
    svc := rds.New(sess)
    
    // Generate auth token
    authToken, err := svc.BuildAuthToken(
        "mypostgres.cluster-xyz.us-east-1.rds.amazonaws.com:5432",
        "us-east-1",
        "myuser",
        sess.Config.Credentials,
    )
    
    if err != nil {
        return nil, err
    }
    
    dsn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=require",
        "mypostgres.cluster-xyz.us-east-1.rds.amazonaws.com",
        5432,
        "myuser",
        authToken,
        "mydb",
    )
    
    return sql.Open("postgres", dsn)
}
```

### Redis and AWS

**Amazon ElastiCache for Redis:**
- Fully managed, in-memory data store
- Sub-millisecond latency and massive scale
- Built-in security and compliance

**AWS MemoryDB for Redis:**
- Redis-compatible, durable, in-memory database
- Microsecond read and single-digit millisecond write latency
- Multi-AZ availability and automatic failover

**Integration Examples:**

**Python with ElastiCache:**
```python
# Using redis-py with ElastiCache
import redis
import boto3

# Connection to ElastiCache cluster
def connect_to_elasticache():
    # Get cluster endpoint from AWS
    client = boto3.client('elasticache', region_name='us-east-1')
    response = client.describe_cache_clusters(
        CacheClusterId='my-redis-cluster',
        ShowCacheNodeInfo=True
    )
    
    endpoint = response['CacheClusters'][0]['CacheNodes'][0]['Endpoint']
    
    r = redis.Redis(
        host=endpoint['Address'],
        port=endpoint['Port'],
        decode_responses=True
    )
    return r

# Using AWS GLIDE for Redis
from glide import RedisClient, RedisClientConfiguration

async def connect_with_glide():
    config = RedisClientConfiguration(
        addresses=[("my-cluster.cache.amazonaws.com", 6379)]
    )
    client = await RedisClient.create(config)
    return client
```

**Go with ElastiCache:**
```go
// Using go-redis with ElastiCache
import (
    "github.com/go-redis/redis/v8"
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/elasticache"
)

func ConnectToElastiCache() (*redis.Client, error) {
    sess := session.Must(session.NewSession())
    svc := elasticache.New(sess)
    
    // Get cluster endpoint
    result, err := svc.DescribeCacheClusters(&elasticache.DescribeCacheClustersInput{
        CacheClusterId:    aws.String("my-redis-cluster"),
        ShowCacheNodeInfo: aws.Bool(true),
    })
    
    if err != nil {
        return nil, err
    }
    
    endpoint := result.CacheClusters[0].CacheNodes[0].Endpoint
    
    rdb := redis.NewClient(&redis.Options{
        Addr: fmt.Sprintf("%s:%d", *endpoint.Address, *endpoint.Port),
    })
    
    return rdb, nil
}
```

**JavaScript with ElastiCache:**
```javascript
// Using ioredis with ElastiCache
const Redis = require('ioredis');
const AWS = require('aws-sdk');

async function connectToElastiCache() {
    const elasticache = new AWS.ElastiCache({ region: 'us-east-1' });
    
    const params = {
        CacheClusterId: 'my-redis-cluster',
        ShowCacheNodeInfo: true
    };
    
    const data = await elasticache.describeCacheClusters(params).promise();
    const endpoint = data.CacheClusters[0].CacheNodes[0].Endpoint;
    
    const redis = new Redis({
        host: endpoint.Address,
        port: endpoint.Port,
        retryDelayOnFailover: 100,
        enableReadyCheck: false,
        maxRetriesPerRequest: 1,
    });
    
    return redis;
}

// Using AWS GLIDE for Redis (Node.js)
const { GlideClient, GlideClientConfiguration } = require('@aws/glide-for-redis');

async function connectWithGlide() {
    const config = new GlideClientConfiguration({
        addresses: [{ host: 'my-cluster.cache.amazonaws.com', port: 6379 }]
    });
    
    const client = await GlideClient.create(config);
    return client;
}
```

## IoT Use Cases

### Real-time Sensor Data Processing
- **Redis**: Cache frequently accessed sensor readings
- **MongoDB**: Store flexible sensor data documents
- **PostgreSQL**: Time-series data analysis with proper indexing

### Device Management
- **MongoDB**: Store device configurations and metadata
- **PostgreSQL**: User accounts, permissions, and relationships
- **Redis**: Session management and real-time device status

### Analytics and Reporting
- **PostgreSQL**: Complex analytical queries and reporting
- **MongoDB**: Aggregation pipelines for data analysis
- **Redis**: Real-time dashboards and metrics caching

## Best Practices

### Security
- Use environment variables for database credentials
- Implement proper authentication and authorization
- Enable SSL/TLS connections
- Regular security updates and patches

### Performance
- Implement connection pooling
- Use appropriate indexing strategies
- Cache frequently accessed data in Redis
- Monitor query performance and optimize

### Scalability
- Design for horizontal scaling
- Use database sharding when appropriate
- Implement proper caching strategies
- Monitor resource usage and plan capacity

## References and Additional Resources

### MongoDB Resources
- [MongoDB Official Documentation](https://docs.mongodb.com/)
- [MongoDB University](https://university.mongodb.com/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Getting Started With MongoDB and AWS CodeWhisperer](https://www.mongodb.com/company/blog/technical/getting-started-with-mongodb-and-codewhisperer)
- [AWS and MongoDB Partnership](https://aws.amazon.com/partners/mongodb/)
- [Amazon DocumentDB Documentation](https://docs.aws.amazon.com/documentdb/)
- [Connecting programmatically to Amazon DocumentDB](https://docs.aws.amazon.com/documentdb/latest/developerguide/connect_programmatically.html)

### PostgreSQL Resources
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Amazon RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/)
- [Amazon Aurora PostgreSQL](https://aws.amazon.com/rds/aurora/postgresql-features/)
- [Connecting to RDS for PostgreSQL with AWS Python Driver](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Connecting.PythonDriver.html)
- [Connecting to PostgreSQL DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToPostgreSQLInstance.html)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [PostGIS for Spatial Data](https://postgis.net/)

### Redis Resources
- [Redis Official Documentation](https://redis.io/documentation)
- [Amazon ElastiCache for Redis](https://aws.amazon.com/elasticache/redis/)
- [Amazon MemoryDB for Redis](https://aws.amazon.com/memorydb/)
- [Python and ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/ElastiCache-Getting-Started-Tutorials-Python.html)
- [Getting started with Python and ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/ElastiCache-Getting-Started-Tutorials.html)
- [Redis Labs University](https://university.redislabs.com/)
- [AWS GLIDE for Redis](https://github.com/aws/glide-for-redis)

### Programming Language Drivers
- **Go**: [mongo-driver](https://pkg.go.dev/go.mongodb.org/mongo-driver), [pq](https://pkg.go.dev/github.com/lib/pq), [go-redis](https://pkg.go.dev/github.com/go-redis/redis)
- **Python**: [pymongo](https://pymongo.readthedocs.io/), [psycopg2](https://www.psycopg.org/), [redis-py](https://redis-py.readthedocs.io/)
- **JavaScript**: [mongodb](https://www.npmjs.com/package/mongodb), [pg](https://www.npmjs.com/package/pg), [ioredis](https://www.npmjs.com/package/ioredis)
- **Java**: [MongoDB Java Driver](https://mongodb.github.io/mongo-java-driver/), [PostgreSQL JDBC](https://jdbc.postgresql.org/), [Jedis](https://github.com/redis/jedis)

### AWS SDK Documentation
- [AWS SDK for Go](https://aws.amazon.com/sdk-for-go/)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS SDK for JavaScript](https://aws.amazon.com/sdk-for-javascript/)
- [AWS SDK for Java](https://aws.amazon.com/sdk-for-java/)

### IoT and Database Integration
- [AWS IoT Core](https://aws.amazon.com/iot-core/)
- [Building IoT Applications with MongoDB](https://www.mongodb.com/solutions/internet-of-things)
- [Time Series Data in PostgreSQL](https://www.timescale.com/)
- [Redis for IoT Applications](https://redis.io/docs/stack/timeseries/)

---

