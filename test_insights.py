import psycopg2
from datetime import datetime, timedelta

def test_database_connection():
    """Test database connection and data fetching"""
    try:
        conn = psycopg2.connect(
            dbname="mydatabase",
            user="postgres",
            password="marco",
            host="localhost",
            port="5432"
        )
        print("✅ Database connection successful")
        
        cursor = conn.cursor()
        
        # Test 1: Check if device table exists and has data
        cursor.execute("SELECT COUNT(*) FROM device")
        device_count = cursor.fetchone()[0]
        print(f"📊 Found {device_count} devices in database")
        
        # Test 2: Check if device_usage table exists and has data
        cursor.execute("SELECT COUNT(*) FROM device_usage")
        usage_count = cursor.fetchone()[0]
        print(f"📊 Found {usage_count} usage records in database")
        
        # Test 3: Get sample data
        if device_count > 0:
            cursor.execute("SELECT name, type, rating, unit FROM device LIMIT 3")
            devices = cursor.fetchall()
            print("\n📋 Sample devices:")
            for device in devices:
                print(f"  - {device[0]} ({device[1]}): {device[2]} {device[3]}")
        
        if usage_count > 0:
            cursor.execute("""
                SELECT d.name, du.date, du.hours_used, (du.hours_used * d.rating) as total_usage
                FROM device_usage du
                JOIN device d ON du.device_id = d.id
                ORDER BY du.date DESC
                LIMIT 5
            """)
            usage_records = cursor.fetchall()
            print("\n📋 Sample usage records:")
            for record in usage_records:
                print(f"  - {record[0]} on {record[1]}: {record[2]} hours = {record[3]:.2f} units")
        
        cursor.close()
        conn.close()
        print("\n✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    print("🔍 Testing Database Connection and Data Fetching")
    print("=" * 50)
    test_database_connection() 