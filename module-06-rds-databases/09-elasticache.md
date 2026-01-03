# 09 - Amazon ElastiCache

## What is ElastiCache?

Amazon ElastiCache is a fully managed in-memory data store and cache service. It provides sub-millisecond latency for caching frequently accessed data, session stores, real-time analytics, and more.

```
+--------------------------------------------------------------------------------+
|                         ELASTICACHE OVERVIEW                                    |
|                                                                                 |
|  +-------------------------+         +-------------------------+               |
|  |       REDIS             |         |      MEMCACHED          |               |
|  +-------------------------+         +-------------------------+               |
|  |                         |         |                         |               |
|  | - Complex data types    |         | - Simple key-value      |               |
|  | - Persistence           |         | - Multi-threaded        |               |
|  | - Replication           |         | - No persistence        |               |
|  | - Pub/Sub               |         | - No replication        |               |
|  | - Transactions          |         | - Simpler architecture  |               |
|  | - Lua scripting         |         | - Lower memory overhead |               |
|  | - Geospatial            |         | - Horizontal scaling    |               |
|  | - Cluster mode          |         |                         |               |
|  |                         |         |                         |               |
|  +-------------------------+         +-------------------------+               |
|                                                                                 |
|                      COMMON USE CASES                                           |
|  +------------------------------------------------------------------+          |
|  | - Database query caching                                         |          |
|  | - Session stores                                                 |          |
|  | - Real-time analytics                                            |          |
|  | - Leaderboards and counting                                      |          |
|  | - Message queues (Redis)                                         |          |
|  | - Pub/Sub messaging (Redis)                                      |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Redis vs Memcached

### Feature Comparison

| Feature | Redis | Memcached |
|---------|-------|-----------|
| **Data Types** | Strings, Lists, Sets, Sorted Sets, Hashes, Bitmaps, Streams | Strings only |
| **Persistence** | Yes (RDB, AOF) | No |
| **Replication** | Yes (primary-replica) | No |
| **Multi-AZ** | Yes (with auto-failover) | No |
| **Cluster Mode** | Yes (sharding) | Yes (client-side sharding) |
| **Pub/Sub** | Yes | No |
| **Transactions** | Yes (MULTI/EXEC) | No |
| **Lua Scripting** | Yes | No |
| **Geospatial** | Yes | No |
| **Maximum Node Size** | 635.61 GiB | 635.61 GiB |
| **Threading** | Single-threaded (I/O threads in 6.0+) | Multi-threaded |
| **Memory Efficiency** | Higher overhead | Lower overhead |

### When to Choose Each

```
+--------------------------------------------------------------------------------+
|                         CHOOSE REDIS WHEN:                                      |
|                                                                                 |
| - You need complex data structures (lists, sets, sorted sets, hashes)          |
| - Data persistence is required                                                  |
| - You need replication for high availability                                    |
| - You're implementing pub/sub messaging                                         |
| - You need transactions or atomic operations                                    |
| - Geospatial data support is needed                                            |
| - You want Lua scripting for complex operations                                |
| - Real-time analytics with sorted sets                                          |
|                                                                                 |
+--------------------------------------------------------------------------------+
|                         CHOOSE MEMCACHED WHEN:                                  |
|                                                                                 |
| - Simple key-value caching is sufficient                                        |
| - You need multi-threaded performance                                           |
| - Memory efficiency is critical                                                 |
| - You're scaling horizontally with simple sharding                             |
| - Persistence and replication aren't needed                                    |
| - Lower latency for simple operations                                           |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## ElastiCache Architecture

### Redis Architecture

```
+--------------------------------------------------------------------------------+
|                     REDIS CLUSTER MODE DISABLED                                 |
|                                                                                 |
|  +------------------------------------------------------------------+          |
|  |                     REPLICATION GROUP                             |          |
|  |                                                                   |          |
|  |   Primary Endpoint: myredis.abc123.ng.0001.use1.cache.amazonaws.com         |
|  |   Reader Endpoint:  myredis-ro.abc123.ng.0001.use1.cache.amazonaws.com      |
|  |                                                                   |          |
|  |          +----------------+                                       |          |
|  |          |   PRIMARY      |                                       |          |
|  |          |   (Read/Write) |                                       |          |
|  |          +-------+--------+                                       |          |
|  |                  |                                                |          |
|  |      +-----------+------------+                                   |          |
|  |      |                        |                                   |          |
|  |      v                        v                                   |          |
|  | +---------+            +---------+                                |          |
|  | | REPLICA |            | REPLICA |                                |          |
|  | | (Read)  |            | (Read)  |                                |          |
|  | +---------+            +---------+                                |          |
|  |    AZ-A                   AZ-B                                    |          |
|  |                                                                   |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  - Single shard with up to 5 replicas                                          |
|  - Up to 635 GiB data (limited by largest node)                               |
|  - Automatic failover to replica if primary fails                              |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

```
+--------------------------------------------------------------------------------+
|                      REDIS CLUSTER MODE ENABLED                                 |
|                                                                                 |
|  +------------------------------------------------------------------+          |
|  |                     CLUSTER (3 SHARDS)                            |          |
|  |                                                                   |          |
|  |   Configuration Endpoint: myredis.abc123.clustercfg.use1.cache.amazonaws.com|
|  |                                                                   |          |
|  |  +----------------+  +----------------+  +----------------+       |          |
|  |  |    SHARD 1     |  |    SHARD 2     |  |    SHARD 3     |       |          |
|  |  | (Slots 0-5460) |  |(Slots 5461-10922)|(Slots 10923-16383)|     |          |
|  |  +----------------+  +----------------+  +----------------+       |          |
|  |  | Primary | Repl |  | Primary | Repl |  | Primary | Repl |       |          |
|  |  +----+----+--+---+  +----+----+--+---+  +----+----+--+---+       |          |
|  |       |       |           |       |           |       |           |          |
|  |       v       v           v       v           v       v           |          |
|  |    +-----+ +-----+     +-----+ +-----+     +-----+ +-----+        |          |
|  |    |Node | |Node |     |Node | |Node |     |Node | |Node |        |          |
|  |    |1a   | |1b   |     |2a   | |2b   |     |3a   | |3b   |        |          |
|  |    +-----+ +-----+     +-----+ +-----+     +-----+ +-----+        |          |
|  |     AZ-A    AZ-B        AZ-A    AZ-B        AZ-A    AZ-B          |          |
|  |                                                                   |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  - Data partitioned across shards using hash slots (16,384 total)             |
|  - Each shard has 1 primary + up to 5 replicas                                |
|  - Scale horizontally by adding shards                                         |
|  - Up to 500 nodes per cluster                                                 |
|  - Maximum ~6.5 TB across cluster                                              |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Memcached Architecture

```
+--------------------------------------------------------------------------------+
|                       MEMCACHED CLUSTER                                         |
|                                                                                 |
|  +------------------------------------------------------------------+          |
|  |                                                                   |          |
|  |   Configuration Endpoint: mymemcached.abc123.cfg.use1.cache.amazonaws.com   |
|  |                                                                   |          |
|  |    +----------+    +----------+    +----------+    +----------+   |          |
|  |    |  Node 1  |    |  Node 2  |    |  Node 3  |    |  Node 4  |   |          |
|  |    | (Cache)  |    | (Cache)  |    | (Cache)  |    | (Cache)  |   |          |
|  |    +----------+    +----------+    +----------+    +----------+   |          |
|  |       AZ-A            AZ-B            AZ-A            AZ-B        |          |
|  |                                                                   |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  CLIENT-SIDE SHARDING:                                                         |
|  +------------------------------------------------------------------+          |
|  |                                                                   |          |
|  |    Application                                                    |          |
|  |        |                                                          |          |
|  |        v                                                          |          |
|  |  +------------+                                                   |          |
|  |  | Memcached  |  Hash(key) % 4 = 0 --> Node 1                   |          |
|  |  | Client     |  Hash(key) % 4 = 1 --> Node 2                   |          |
|  |  | Library    |  Hash(key) % 4 = 2 --> Node 3                   |          |
|  |  +------------+  Hash(key) % 4 = 3 --> Node 4                   |          |
|  |                                                                   |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  - No replication (if node fails, data is lost)                               |
|  - Client handles consistent hashing                                           |
|  - Easy horizontal scaling (add/remove nodes)                                  |
|  - Auto Discovery for node changes                                             |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Caching Strategies

### Lazy Loading (Cache-Aside)

```
+--------------------------------------------------------------------------------+
|                         LAZY LOADING                                            |
|                                                                                 |
|  READ OPERATION:                                                                |
|                                                                                 |
|  +-------------+      1. Get       +--------------+                            |
|  | Application | ----------------> |    Cache     |                            |
|  +-------------+                   +--------------+                            |
|        |                                  |                                     |
|        |                           2a. Cache HIT                               |
|        |                           Return data                                  |
|        |                                  |                                     |
|        |                           2b. Cache MISS                              |
|        |                                  |                                     |
|        | 3. Get from DB                   |                                     |
|        v                                  |                                     |
|  +--------------+                         |                                     |
|  |   Database   |                         |                                     |
|  +--------------+                         |                                     |
|        |                                  |                                     |
|        | 4. Return data                   |                                     |
|        |                                  |                                     |
|  +-----v-------+     5. Update cache      |                                     |
|  | Application | ------------------------>|                                     |
|  +-------------+                          |                                     |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

```python
import redis
import json
import mysql.connector

# Initialize Redis client
cache = redis.Redis(host='mycluster.abc123.use1.cache.amazonaws.com', port=6379)

def get_user(user_id):
    """Lazy loading with cache-aside pattern"""
    cache_key = f"user:{user_id}"

    # Step 1: Try to get from cache
    cached_data = cache.get(cache_key)

    if cached_data:
        # Cache HIT - return cached data
        print(f"Cache HIT for {cache_key}")
        return json.loads(cached_data)

    # Cache MISS - get from database
    print(f"Cache MISS for {cache_key}")

    # Step 2: Query database
    db = mysql.connector.connect(host='mydb.rds.amazonaws.com', user='admin', password='pass', database='myapp')
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        # Step 3: Store in cache with TTL
        cache.setex(cache_key, 3600, json.dumps(user))  # 1 hour TTL

    return user

# Usage
user = get_user(123)
```

**Pros:**
- Only requested data is cached
- Resilient to cache failures (falls back to DB)
- Simple to implement

**Cons:**
- Cache miss penalty (extra round trip)
- Stale data possible (until TTL expires)

### Write-Through

```
+--------------------------------------------------------------------------------+
|                         WRITE-THROUGH                                           |
|                                                                                 |
|  WRITE OPERATION:                                                               |
|                                                                                 |
|  +-------------+     1. Write      +--------------+                            |
|  | Application | ----------------> |    Cache     |                            |
|  +-------------+                   +--------------+                            |
|                                          |                                      |
|                                    2. Write to DB                              |
|                                          |                                      |
|                                          v                                      |
|                                   +--------------+                             |
|                                   |   Database   |                             |
|                                   +--------------+                             |
|                                          |                                      |
|                                    3. Confirm                                   |
|                                          |                                      |
|                                          v                                      |
|                                   +-------------+                              |
|                                   | Application |                              |
|                                   | (success)   |                              |
|                                   +-------------+                              |
|                                                                                 |
|  Data is always written to BOTH cache and database                             |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

```python
import redis
import json
import mysql.connector

cache = redis.Redis(host='mycluster.abc123.use1.cache.amazonaws.com', port=6379)

def update_user(user_id, user_data):
    """Write-through pattern"""
    cache_key = f"user:{user_id}"

    # Step 1: Write to database first
    db = mysql.connector.connect(host='mydb.rds.amazonaws.com', user='admin', password='pass', database='myapp')
    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET name = %s, email = %s WHERE user_id = %s",
        (user_data['name'], user_data['email'], user_id)
    )
    db.commit()
    cursor.close()
    db.close()

    # Step 2: Update cache
    cache.setex(cache_key, 3600, json.dumps(user_data))

    return True

def create_user(user_data):
    """Write-through for new data"""
    # Write to database
    db = mysql.connector.connect(host='mydb.rds.amazonaws.com', user='admin', password='pass', database='myapp')
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (user_data['name'], user_data['email'])
    )
    user_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()

    # Write to cache
    cache_key = f"user:{user_id}"
    user_data['user_id'] = user_id
    cache.setex(cache_key, 3600, json.dumps(user_data))

    return user_id
```

**Pros:**
- Cache is always up-to-date
- No stale data
- Reads are always fast (data already cached)

**Cons:**
- Higher write latency (two writes)
- Cache filled with potentially unused data
- More complex implementation

### Write-Behind (Write-Back)

```
+--------------------------------------------------------------------------------+
|                         WRITE-BEHIND                                            |
|                                                                                 |
|  WRITE OPERATION:                                                               |
|                                                                                 |
|  +-------------+     1. Write      +--------------+                            |
|  | Application | ----------------> |    Cache     |                            |
|  +-------------+                   +--------------+                            |
|        |                                  |                                     |
|        | 2. Immediate                     |                                     |
|        |    ACK                     3. Async write                             |
|        v                            (batched)                                   |
|  +-------------+                          |                                     |
|  | Application |                          v                                     |
|  | continues   |                   +--------------+                            |
|  +-------------+                   |   Database   |                            |
|                                    +--------------+                            |
|                                                                                 |
|  Writes are acknowledged immediately, database updated asynchronously          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

**Pros:**
- Lowest write latency
- Batch writes to database
- Reduce database load

**Cons:**
- Risk of data loss if cache fails before DB write
- Complex to implement correctly
- Eventual consistency

### Combined Strategy (Recommended)

```python
import redis
import json
from functools import wraps

cache = redis.Redis(host='mycluster.abc123.use1.cache.amazonaws.com', port=6379)

class CacheManager:
    def __init__(self, cache_client, default_ttl=3600):
        self.cache = cache_client
        self.default_ttl = default_ttl

    def get_or_set(self, key, fetch_func, ttl=None):
        """Lazy loading pattern"""
        cached = self.cache.get(key)
        if cached:
            return json.loads(cached)

        data = fetch_func()
        if data:
            self.cache.setex(key, ttl or self.default_ttl, json.dumps(data))
        return data

    def write_through(self, key, data, write_func, ttl=None):
        """Write-through pattern"""
        # Write to database
        result = write_func(data)

        # Update cache
        if result:
            self.cache.setex(key, ttl or self.default_ttl, json.dumps(data))

        return result

    def invalidate(self, key):
        """Invalidate cache entry"""
        self.cache.delete(key)

    def invalidate_pattern(self, pattern):
        """Invalidate all keys matching pattern"""
        keys = self.cache.keys(pattern)
        if keys:
            self.cache.delete(*keys)

# Usage example
cache_manager = CacheManager(cache)

# Lazy loading
def fetch_user_from_db(user_id):
    # Database query here
    return {'user_id': user_id, 'name': 'John'}

user = cache_manager.get_or_set(
    f"user:123",
    lambda: fetch_user_from_db(123)
)

# Write-through with invalidation
def update_user_in_db(user_data):
    # Database update here
    return True

cache_manager.write_through(
    f"user:123",
    {'user_id': 123, 'name': 'Updated Name'},
    lambda data: update_user_in_db(data)
)
```

## Redis Data Types and Operations

### Strings

```python
import redis

r = redis.Redis(host='mycluster.use1.cache.amazonaws.com', port=6379)

# Basic operations
r.set('user:1:name', 'John Doe')
name = r.get('user:1:name')  # b'John Doe'

# With expiration
r.setex('session:abc123', 3600, 'user_data')  # Expires in 1 hour

# Atomic increment (counters)
r.set('page:views', 0)
r.incr('page:views')        # 1
r.incrby('page:views', 10)  # 11

# Multiple keys
r.mset({'key1': 'value1', 'key2': 'value2'})
values = r.mget(['key1', 'key2'])  # [b'value1', b'value2']
```

### Lists

```python
# Queue pattern (FIFO)
r.lpush('queue:tasks', 'task1', 'task2', 'task3')
task = r.rpop('queue:tasks')  # 'task1'

# Stack pattern (LIFO)
r.lpush('stack:undo', 'action1', 'action2')
action = r.lpop('stack:undo')  # 'action2'

# Get range
r.lpush('recent:views', 'page1', 'page2', 'page3')
recent = r.lrange('recent:views', 0, 4)  # Last 5 items

# Trim list (keep only last N items)
r.ltrim('recent:views', 0, 99)  # Keep only 100 items
```

### Sets

```python
# User interests
r.sadd('user:1:interests', 'python', 'aws', 'databases')
r.sadd('user:2:interests', 'python', 'javascript', 'react')

# Check membership
r.sismember('user:1:interests', 'python')  # True

# Set operations
common = r.sinter('user:1:interests', 'user:2:interests')  # {'python'}
all_interests = r.sunion('user:1:interests', 'user:2:interests')

# Random member
random_interest = r.srandmember('user:1:interests')
```

### Sorted Sets (Leaderboards)

```python
# Gaming leaderboard
r.zadd('leaderboard:game1', {'player1': 100, 'player2': 200, 'player3': 150})

# Get top 10 players (highest scores first)
top_10 = r.zrevrange('leaderboard:game1', 0, 9, withscores=True)
# [('player2', 200.0), ('player3', 150.0), ('player1', 100.0)]

# Get player rank (0-indexed, highest = 0)
rank = r.zrevrank('leaderboard:game1', 'player1')  # 2

# Increment score
r.zincrby('leaderboard:game1', 50, 'player1')  # New score: 150

# Get players within score range
players = r.zrangebyscore('leaderboard:game1', 100, 200)
```

### Hashes

```python
# User profile as hash
r.hset('user:1', mapping={
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30,
    'city': 'New York'
})

# Get all fields
user = r.hgetall('user:1')
# {b'name': b'John Doe', b'email': b'john@example.com', ...}

# Get specific fields
name = r.hget('user:1', 'name')

# Update field
r.hset('user:1', 'age', 31)

# Increment numeric field
r.hincrby('user:1', 'age', 1)
```

### Pub/Sub

```python
import redis
import threading

r = redis.Redis(host='mycluster.use1.cache.amazonaws.com', port=6379)

# Subscriber
def subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe('notifications')

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received: {message['data']}")

# Start subscriber in background
thread = threading.Thread(target=subscriber)
thread.daemon = True
thread.start()

# Publisher
r.publish('notifications', 'New order received!')
r.publish('notifications', 'Payment processed!')
```

## Hands-On: Creating ElastiCache Clusters

### Redis Cluster (AWS CLI)

```bash
# Create subnet group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name my-redis-subnet \
    --cache-subnet-group-description "Subnet group for Redis" \
    --subnet-ids subnet-abc123 subnet-def456

# Create Redis cluster (cluster mode disabled)
aws elasticache create-replication-group \
    --replication-group-id my-redis-cluster \
    --replication-group-description "Redis cluster for caching" \
    --engine redis \
    --engine-version 7.0 \
    --cache-node-type cache.r6g.large \
    --num-cache-clusters 3 \
    --automatic-failover-enabled \
    --multi-az-enabled \
    --cache-subnet-group-name my-redis-subnet \
    --security-group-ids sg-12345678 \
    --at-rest-encryption-enabled \
    --transit-encryption-enabled \
    --auth-token "MySecurePassword123!"

# Create Redis cluster (cluster mode enabled)
aws elasticache create-replication-group \
    --replication-group-id my-redis-sharded \
    --replication-group-description "Sharded Redis cluster" \
    --engine redis \
    --engine-version 7.0 \
    --cache-node-type cache.r6g.large \
    --num-node-groups 3 \
    --replicas-per-node-group 2 \
    --automatic-failover-enabled \
    --multi-az-enabled \
    --cache-subnet-group-name my-redis-subnet \
    --security-group-ids sg-12345678
```

### Memcached Cluster (AWS CLI)

```bash
# Create Memcached cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id my-memcached-cluster \
    --engine memcached \
    --engine-version 1.6.17 \
    --cache-node-type cache.r6g.large \
    --num-cache-nodes 3 \
    --cache-subnet-group-name my-cache-subnet \
    --security-group-ids sg-12345678 \
    --az-mode cross-az \
    --preferred-availability-zones us-east-1a us-east-1b us-east-1c
```

### Python Connection Examples

```python
# Redis connection
import redis

# Cluster mode disabled (single endpoint)
r = redis.Redis(
    host='my-redis-cluster.abc123.use1.cache.amazonaws.com',
    port=6379,
    password='MySecurePassword123!',
    ssl=True,
    ssl_cert_reqs=None
)

# Cluster mode enabled
from redis.cluster import RedisCluster

rc = RedisCluster(
    host='my-redis-sharded.abc123.clustercfg.use1.cache.amazonaws.com',
    port=6379,
    password='MySecurePassword123!',
    ssl=True,
    ssl_cert_reqs=None
)

# Memcached connection
from pymemcache.client.hash import HashClient

memcached = HashClient([
    ('node1.abc123.use1.cache.amazonaws.com', 11211),
    ('node2.abc123.use1.cache.amazonaws.com', 11211),
    ('node3.abc123.use1.cache.amazonaws.com', 11211)
])
```

## Session Store Implementation

### Flask with Redis Sessions

```python
from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)

# Configure Redis session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(
    host='my-redis-cluster.abc123.use1.cache.amazonaws.com',
    port=6379,
    password='MySecurePassword123!',
    ssl=True
)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

Session(app)

@app.route('/login')
def login():
    session['user_id'] = 123
    session['username'] = 'john_doe'
    return 'Logged in!'

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return 'Not logged in', 401
    return f'User ID: {user_id}'

@app.route('/logout')
def logout():
    session.clear()
    return 'Logged out!'
```

### Django with Redis Cache

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'rediss://my-redis-cluster.abc123.use1.cache.amazonaws.com:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': 'MySecurePassword123!',
            'SSL': True,
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# views.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page

# Manual caching
def get_user_data(user_id):
    cache_key = f'user:{user_id}'
    data = cache.get(cache_key)

    if data is None:
        data = User.objects.get(id=user_id).to_dict()
        cache.set(cache_key, data, timeout=3600)

    return data

# View caching decorator
@cache_page(60 * 15)  # Cache for 15 minutes
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})
```

## Performance Tuning

### Redis Configuration

```bash
# Parameter group settings for production
aws elasticache create-cache-parameter-group \
    --cache-parameter-group-family redis7 \
    --cache-parameter-group-name my-redis-params \
    --description "Custom Redis parameters"

# Modify parameters
aws elasticache modify-cache-parameter-group \
    --cache-parameter-group-name my-redis-params \
    --parameter-name-values \
        "ParameterName=maxmemory-policy,ParameterValue=allkeys-lru" \
        "ParameterName=timeout,ParameterValue=300" \
        "ParameterName=tcp-keepalive,ParameterValue=300"
```

### Memory Policies

| Policy | Description | Use Case |
|--------|-------------|----------|
| `noeviction` | Return error when memory limit reached | When data loss is unacceptable |
| `allkeys-lru` | Evict least recently used keys | General caching |
| `volatile-lru` | Evict LRU keys with TTL set | Mixed usage (permanent + cached) |
| `allkeys-lfu` | Evict least frequently used keys | When access patterns vary |
| `volatile-ttl` | Evict keys with shortest TTL | Time-sensitive data |
| `allkeys-random` | Random eviction | When all keys equal importance |

### Monitoring Metrics

```
+--------------------------------------------------------------------------------+
|                      KEY ELASTICACHE METRICS                                    |
|                                                                                 |
|  MEMORY:                                                                        |
|  - BytesUsedForCache: Memory used by cache                                     |
|  - DatabaseMemoryUsagePercentage: % of memory used                             |
|  - Evictions: Number of keys evicted due to memory pressure                    |
|                                                                                 |
|  PERFORMANCE:                                                                   |
|  - CacheHits: Successful key lookups                                           |
|  - CacheMisses: Failed key lookups                                             |
|  - CacheHitRate: CacheHits / (CacheHits + CacheMisses)                        |
|  - CurrConnections: Current client connections                                 |
|                                                                                 |
|  CPU:                                                                           |
|  - CPUUtilization: % CPU used                                                  |
|  - EngineCPUUtilization: % CPU used by Redis engine                           |
|                                                                                 |
|  REPLICATION:                                                                   |
|  - ReplicationLag: Seconds behind primary (replicas)                           |
|  - ReplicationBytes: Bytes replicated                                          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### CloudWatch Alarms

```bash
# Create alarm for high memory usage
aws cloudwatch put-metric-alarm \
    --alarm-name redis-high-memory \
    --alarm-description "Redis memory usage above 80%" \
    --metric-name DatabaseMemoryUsagePercentage \
    --namespace AWS/ElastiCache \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=CacheClusterId,Value=my-redis-cluster \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts

# Create alarm for low cache hit rate
aws cloudwatch put-metric-alarm \
    --alarm-name redis-low-hit-rate \
    --alarm-description "Cache hit rate below 80%" \
    --metric-name CacheHitRate \
    --namespace AWS/ElastiCache \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator LessThanThreshold \
    --dimensions Name=CacheClusterId,Value=my-redis-cluster \
    --evaluation-periods 3 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

## Security Best Practices

### Network Security

```
+--------------------------------------------------------------------------------+
|                     ELASTICACHE SECURITY                                        |
|                                                                                 |
|  +------------------------------------------------------------------+          |
|  |                          VPC                                      |          |
|  |                                                                   |          |
|  |   Private Subnet                     Private Subnet               |          |
|  |   +------------------+               +------------------+         |          |
|  |   |  ElastiCache     |               |   Application    |         |          |
|  |   |  (Redis/Memcached)|<------------>|   Servers        |         |          |
|  |   +------------------+               +------------------+         |          |
|  |          |                                   |                    |          |
|  |          | Security Group                    |                    |          |
|  |          | - Allow port 6379/11211           |                    |          |
|  |          | - Only from app security group    |                    |          |
|  |                                                                   |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  NEVER expose ElastiCache to the internet!                                     |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Encryption

```bash
# Create Redis with encryption
aws elasticache create-replication-group \
    --replication-group-id secure-redis \
    --engine redis \
    --at-rest-encryption-enabled \
    --transit-encryption-enabled \
    --auth-token "StrongPassword123!" \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abc123
```

### IAM Authentication (Redis 7.0+)

```python
import boto3
import redis
from botocore.signers import RequestSigner

def get_elasticache_auth_token(cluster_name, region='us-east-1'):
    """Generate IAM auth token for ElastiCache"""
    session = boto3.Session()
    credentials = session.get_credentials()
    signer = RequestSigner(
        'elasticache',
        region,
        'elasticache',
        'v4',
        credentials,
        session.events
    )

    url = f"{cluster_name}.{region}.cache.amazonaws.com:6379"
    signed_url = signer.generate_presigned_url(
        {'method': 'GET', 'url': url},
        operation_name='connect',
        expires_in=900
    )

    return signed_url.split('?')[1]

# Connect with IAM auth
auth_token = get_elasticache_auth_token('my-redis-cluster')
r = redis.Redis(
    host='my-redis-cluster.abc123.use1.cache.amazonaws.com',
    port=6379,
    password=auth_token,
    ssl=True
)
```

## Summary

### ElastiCache Decision Guide

```
+--------------------------------------------------------------------------------+
|                                                                                 |
|  Need complex data types (lists, sets, hashes)? --> REDIS                     |
|                                                                                 |
|  Need persistence/durability? --> REDIS                                        |
|                                                                                 |
|  Need replication/high availability? --> REDIS                                 |
|                                                                                 |
|  Need pub/sub messaging? --> REDIS                                             |
|                                                                                 |
|  Simple key-value caching only? --> MEMCACHED (or REDIS)                      |
|                                                                                 |
|  Need multi-threading? --> MEMCACHED                                           |
|                                                                                 |
|  When in doubt --> REDIS (more features, same or better performance)          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Best Practices Checklist

- [ ] Deploy in private subnets only
- [ ] Use security groups to restrict access
- [ ] Enable encryption at rest and in transit
- [ ] Use AUTH tokens for Redis
- [ ] Implement proper TTL strategies
- [ ] Monitor cache hit rates
- [ ] Set up CloudWatch alarms
- [ ] Use appropriate eviction policies
- [ ] Size instances based on memory needs
- [ ] Use cluster mode for horizontal scaling

---

**Next:** [10 - Database Migration](./10-database-migration.md)

**Previous:** [08 - DynamoDB](./08-dynamodb.md)
