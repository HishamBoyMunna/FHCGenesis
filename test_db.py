import psycopg2
import sys

try:
    print("Attempting to connect to the database...")
    conn = psycopg2.connect(
        dbname="mydatabase",
        user="postgres",
        # --- IMPORTANT: CHANGE THIS TO YOUR ACTUAL PASSWORD ---
        password="marco",
        host="localhost",
        port="5432"
    )
    print("✅ Connection successful!")
    conn.close()

except psycopg2.OperationalError as e:
    print("❌ Connection Failed. This is likely a password or permission issue.", file=sys.stderr)
    print(f"   Error: {e}", file=sys.stderr)

except Exception as e:
    print(f"❌ An unexpected error occurred: {e}", file=sys.stderr)