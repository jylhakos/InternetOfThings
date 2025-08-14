#!/bin/bash

# MongoDB Health Check and Monitoring Script
# Usage: ./scripts/mongodb-health.sh {local|atlas|documentdb|ec2|all|help}

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
load_env() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        source "$env_file"
        return 0
    fi
    return 1
}

check_mongosh() {
    if ! command -v mongosh &> /dev/null; then
        print_error "mongosh is not installed. Please install MongoDB Shell."
        echo "Installation: https://docs.mongodb.com/mongodb-shell/install/"
        return 1
    fi
    return 0
}

test_connection() {
    local connection_string="$1"
    local timeout="${2:-10}"
    
    print_status "Testing connection (timeout: ${timeout}s)..."
    
    if timeout "$timeout" mongosh "$connection_string" --quiet --eval "db.adminCommand('ping')" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

get_database_stats() {
    local connection_string="$1"
    local database="$2"
    
    local stats=$(mongosh "$connection_string/$database" --quiet --eval "
        try {
            var stats = db.stats();
            var collections = db.getCollectionNames();
            var userCount = db.users ? db.users.countDocuments() : 0;
            
            print('📊 Database Statistics:');
            print('   Database: ' + db.getName());
            print('   Collections: ' + collections.length);
            print('   Users: ' + userCount);
            print('   Data Size: ' + (stats.dataSize / 1024 / 1024).toFixed(2) + ' MB');
            print('   Storage Size: ' + (stats.storageSize / 1024 / 1024).toFixed(2) + ' MB');
            print('   Indexes: ' + stats.indexes);
            print('   Index Size: ' + (stats.indexSize / 1024 / 1024).toFixed(2) + ' MB');
            
            if (collections.length > 0) {
                print('📋 Collections:');
                collections.forEach(function(col) {
                    var count = db[col].countDocuments();
                    print('   - ' + col + ': ' + count + ' documents');
                });
            }
        } catch(e) {
            print('❌ Error getting stats: ' + e.message);
        }
    " 2>/dev/null)
    
    echo "$stats"
}

check_local() {
    print_status "🔍 Checking Local MongoDB..."
    echo "=================================="
    
    # Check if Docker container is running
    if docker ps --format '{{.Names}}' | grep -q "^mongodb-dev$"; then
        print_success "✅ Docker container is running"
        
        # Test connection
        local connection_string="mongodb://app_user:app_password@localhost:27017/flutter_spa"
        
        if test_connection "$connection_string"; then
            print_success "✅ Database connection successful"
            
            # Get stats
            get_database_stats "$connection_string" "flutter_spa"
            
            # Check disk usage
            local disk_usage=$(docker exec mongodb-dev df -h /data/db | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')
            echo "💾 Disk Usage: $disk_usage"
            
            # Check memory usage
            local memory_usage=$(docker stats mongodb-dev --no-stream --format "table {{.MemUsage}}" | tail -1)
            echo "🧠 Memory Usage: $memory_usage"
            
        else
            print_error "❌ Database connection failed"
            print_status "Container logs (last 10 lines):"
            docker logs mongodb-dev --tail 10
            return 1
        fi
        
    else
        print_error "❌ MongoDB Docker container is not running"
        print_status "Start with: ./scripts/mongodb-dev.sh start"
        return 1
    fi
    
    echo
}

check_atlas() {
    print_status "🔍 Checking MongoDB Atlas..."
    echo "================================"
    
    if ! load_env "./config/mongodb-atlas.env"; then
        print_error "❌ Atlas configuration not found"
        print_status "Deploy with: ./scripts/deploy-mongodb-aws.sh atlas"
        return 1
    fi
    
    if [ -z "$MONGODB_URI" ]; then
        print_error "❌ MONGODB_URI not set in configuration"
        return 1
    fi
    
    print_success "✅ Configuration loaded"
    print_status "🔗 Cluster: $CLUSTER_NAME"
    print_status "👤 Username: $MONGODB_USERNAME"
    
    if test_connection "$MONGODB_URI" 15; then
        print_success "✅ Atlas connection successful"
        
        # Get stats
        get_database_stats "$MONGODB_URI" "$MONGODB_DATABASE"
        
        # Get cluster info if atlas CLI is available
        if command -v atlas &> /dev/null; then
            print_status "📡 Cluster Information:"
            local cluster_info=$(atlas clusters describe "$CLUSTER_NAME" --output json 2>/dev/null | jq -r '
                "   Provider: " + .providerSettings.providerName + 
                "\n   Region: " + .providerSettings.regionName +
                "\n   Tier: " + .providerSettings.instanceSizeName +
                "\n   Disk Size: " + (.providerSettings.diskIOPS | tostring) + " GB" +
                "\n   Status: " + .stateName
            ')
            echo "$cluster_info"
        fi
        
    else
        print_error "❌ Atlas connection failed"
        print_status "Check your network connection and Atlas configuration"
        return 1
    fi
    
    echo
}

check_documentdb() {
    print_status "🔍 Checking AWS DocumentDB..."
    echo "====================================="
    
    if ! load_env "./config/mongodb-documentdb.env"; then
        print_error "❌ DocumentDB configuration not found"
        print_status "Deploy with: ./scripts/deploy-mongodb-aws.sh documentdb"
        return 1
    fi
    
    if [ -z "$MONGODB_URI" ]; then
        print_error "❌ MONGODB_URI not set in configuration"
        return 1
    fi
    
    print_success "✅ Configuration loaded"
    print_status "🌍 Host: $MONGODB_HOST:$MONGODB_PORT"
    print_status "👤 Username: $MONGODB_USERNAME"
    
    # Check if CA certificate exists
    if [ ! -f "$TLS_CA_FILE" ]; then
        print_warning "⚠️  TLS CA file not found: $TLS_CA_FILE"
        print_status "Downloading certificate..."
        mkdir -p "$(dirname "$TLS_CA_FILE")"
        curl -o "$TLS_CA_FILE" https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
    fi
    
    if test_connection "$MONGODB_URI" 20; then
        print_success "✅ DocumentDB connection successful"
        
        # Get stats
        get_database_stats "$MONGODB_URI" "$MONGODB_DATABASE"
        
        # Get cluster info using AWS CLI if available
        if command -v aws &> /dev/null; then
            print_status "📡 Cluster Information:"
            local cluster_info=$(aws docdb describe-db-clusters --db-cluster-identifier "$CLUSTER_NAME" --output json 2>/dev/null | jq -r '
                .DBClusters[0] | 
                "   Engine: " + .Engine + 
                "\n   Version: " + .EngineVersion +
                "\n   Status: " + .Status +
                "\n   Endpoint: " + .Endpoint +
                "\n   Port: " + (.Port | tostring) +
                "\n   Backup Retention: " + (.BackupRetentionPeriod | tostring) + " days"
            ')
            echo "$cluster_info"
        fi
        
    else
        print_error "❌ DocumentDB connection failed"
        print_status "Check your AWS configuration and network access"
        return 1
    fi
    
    echo
}

check_ec2() {
    print_status "🔍 Checking EC2 MongoDB..."
    echo "============================"
    
    if ! load_env "./config/mongodb-ec2.env"; then
        print_error "❌ EC2 configuration not found"
        print_status "Deploy with: ./scripts/deploy-mongodb-aws.sh ec2"
        return 1
    fi
    
    if [ -z "$MONGODB_URI" ]; then
        print_error "❌ MONGODB_URI not set in configuration"
        return 1
    fi
    
    print_success "✅ Configuration loaded"
    print_status "🌍 Host: $MONGODB_HOST:$MONGODB_PORT"
    print_status "👤 Username: $MONGODB_USERNAME"
    
    # Check if instance is running
    if command -v aws &> /dev/null && [ -n "$INSTANCE_ID" ]; then
        local instance_state=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null)
        if [ "$instance_state" = "running" ]; then
            print_success "✅ EC2 instance is running"
        else
            print_warning "⚠️  EC2 instance state: $instance_state"
        fi
    fi
    
    if test_connection "$MONGODB_URI" 15; then
        print_success "✅ EC2 MongoDB connection successful"
        
        # Get stats
        get_database_stats "$MONGODB_URI" "$MONGODB_DATABASE"
        
        # Get instance info
        if command -v aws &> /dev/null && [ -n "$INSTANCE_ID" ]; then
            print_status "💻 Instance Information:"
            local instance_info=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --output json 2>/dev/null | jq -r '
                .Reservations[0].Instances[0] | 
                "   Instance Type: " + .InstanceType +
                "\n   Launch Time: " + .LaunchTime +
                "\n   Public IP: " + .PublicIpAddress +
                "\n   Private IP: " + .PrivateIpAddress +
                "\n   State: " + .State.Name
            ')
            echo "$instance_info"
        fi
        
    else
        print_error "❌ EC2 MongoDB connection failed"
        print_status "Check instance status and security group configuration"
        return 1
    fi
    
    echo
}

backup_database() {
    local environment="$1"
    local backup_dir="./backups/mongodb/$(date +%Y%m%d_%H%M%S)"
    
    print_status "💾 Creating database backup for $environment..."
    
    mkdir -p "$backup_dir"
    
    case "$environment" in
        local)
            if docker ps --format '{{.Names}}' | grep -q "^mongodb-dev$"; then
                docker exec mongodb-dev mongodump --db flutter_spa --out /tmp/backup
                docker cp mongodb-dev:/tmp/backup/flutter_spa "$backup_dir/"
                docker exec mongodb-dev rm -rf /tmp/backup
                print_success "✅ Local backup created: $backup_dir"
            else
                print_error "❌ Local MongoDB container not running"
                return 1
            fi
            ;;
        atlas)
            if load_env "./config/mongodb-atlas.env" && [ -n "$MONGODB_URI" ]; then
                mongodump --uri "$MONGODB_URI" --out "$backup_dir"
                print_success "✅ Atlas backup created: $backup_dir"
            else
                print_error "❌ Atlas configuration not found"
                return 1
            fi
            ;;
        documentdb)
            if load_env "./config/mongodb-documentdb.env" && [ -n "$MONGODB_URI" ]; then
                mongodump --uri "$MONGODB_URI" --ssl --sslCAFile "$TLS_CA_FILE" --out "$backup_dir"
                print_success "✅ DocumentDB backup created: $backup_dir"
            else
                print_error "❌ DocumentDB configuration not found"
                return 1
            fi
            ;;
        ec2)
            if load_env "./config/mongodb-ec2.env" && [ -n "$MONGODB_URI" ]; then
                mongodump --uri "$MONGODB_URI" --out "$backup_dir"
                print_success "✅ EC2 backup created: $backup_dir"
            else
                print_error "❌ EC2 configuration not found"
                return 1
            fi
            ;;
        *)
            print_error "Unknown environment: $environment"
            return 1
            ;;
    esac
    
    # Compress backup
    tar -czf "$backup_dir.tar.gz" -C "$(dirname "$backup_dir")" "$(basename "$backup_dir")"
    rm -rf "$backup_dir"
    print_success "✅ Backup compressed: $backup_dir.tar.gz"
}

performance_test() {
    local environment="$1"
    local connection_string=""
    
    case "$environment" in
        local)
            connection_string="mongodb://app_user:app_password@localhost:27017/flutter_spa"
            ;;
        atlas)
            if load_env "./config/mongodb-atlas.env"; then
                connection_string="$MONGODB_URI"
            fi
            ;;
        documentdb)
            if load_env "./config/mongodb-documentdb.env"; then
                connection_string="$MONGODB_URI"
            fi
            ;;
        ec2)
            if load_env "./config/mongodb-ec2.env"; then
                connection_string="$MONGODB_URI"
            fi
            ;;
    esac
    
    if [ -z "$connection_string" ]; then
        print_error "❌ Could not get connection string for $environment"
        return 1
    fi
    
    print_status "🚀 Running performance test on $environment..."
    
    local test_results=$(mongosh "$connection_string/flutter_spa" --quiet --eval "
        print('⏱️  Performance Test Results:');
        
        // Insert test
        var start = new Date();
        for (var i = 0; i < 100; i++) {
            db.test_performance.insertOne({
                name: 'Test User ' + i,
                email: 'test' + i + '@example.com',
                created: new Date()
            });
        }
        var insertTime = new Date() - start;
        print('   Insert 100 docs: ' + insertTime + 'ms');
        
        // Query test
        start = new Date();
        for (var i = 0; i < 100; i++) {
            db.test_performance.findOne({name: 'Test User ' + Math.floor(Math.random() * 100)});
        }
        var queryTime = new Date() - start;
        print('   Query 100 docs: ' + queryTime + 'ms');
        
        // Update test
        start = new Date();
        for (var i = 0; i < 100; i++) {
            db.test_performance.updateOne({name: 'Test User ' + i}, {\$set: {updated: new Date()}});
        }
        var updateTime = new Date() - start;
        print('   Update 100 docs: ' + updateTime + 'ms');
        
        // Cleanup
        db.test_performance.drop();
        print('   Test data cleaned up');
        
        print('📊 Average per operation:');
        print('   Insert: ' + (insertTime / 100).toFixed(2) + 'ms');
        print('   Query: ' + (queryTime / 100).toFixed(2) + 'ms');
        print('   Update: ' + (updateTime / 100).toFixed(2) + 'ms');
    " 2>/dev/null)
    
    echo "$test_results"
}

show_help() {
    echo "MongoDB Health Check and Monitoring Script"
    echo
    echo "Usage: $0 {local|atlas|documentdb|ec2|all|backup|perf|help}"
    echo
    echo "Commands:"
    echo "  local      - Check local MongoDB (Docker)"
    echo "  atlas      - Check MongoDB Atlas cluster"
    echo "  documentdb - Check AWS DocumentDB cluster"
    echo "  ec2        - Check MongoDB on EC2"
    echo "  all        - Check all configured environments"
    echo "  backup     - Create database backup"
    echo "  perf       - Run performance test"
    echo "  help       - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 local                # Check local MongoDB"
    echo "  $0 atlas                # Check Atlas cluster"
    echo "  $0 all                  # Check all environments"
    echo "  $0 backup local         # Backup local database"
    echo "  $0 perf atlas           # Performance test on Atlas"
    echo
    echo "Prerequisites:"
    echo "  - mongosh (MongoDB Shell) installed"
    echo "  - Appropriate configuration files in ./config/"
    echo "  - Network access to remote databases"
}

# Main script logic
case "$1" in
    local)
        check_mongosh || exit 1
        check_local
        ;;
    atlas)
        check_mongosh || exit 1
        check_atlas
        ;;
    documentdb)
        check_mongosh || exit 1
        check_documentdb
        ;;
    ec2)
        check_mongosh || exit 1
        check_ec2
        ;;
    all)
        check_mongosh || exit 1
        echo "🔍 MongoDB Health Check - All Environments"
        echo "=========================================="
        echo
        
        check_local
        check_atlas
        check_documentdb
        check_ec2
        
        print_success "🎉 Health check complete!"
        ;;
    backup)
        check_mongosh || exit 1
        if [ -z "$2" ]; then
            print_error "Please specify environment: local|atlas|documentdb|ec2"
            exit 1
        fi
        backup_database "$2"
        ;;
    perf)
        check_mongosh || exit 1
        if [ -z "$2" ]; then
            print_error "Please specify environment: local|atlas|documentdb|ec2"
            exit 1
        fi
        performance_test "$2"
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac
