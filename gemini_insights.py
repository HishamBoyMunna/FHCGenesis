import psycopg2
import google.generativeai as genai
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
#GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_KEY = "AIzaSyD2bK8Rov5AQeiFwnevXIux8BeHOtMFoe0"
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_database_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            dbname="mydatabase",
            user="postgres",
            password="marco",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def fetch_device_data():
    """Fetch device ratings and usage data from the database"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Get all devices with their ratings
        cursor.execute("""
            SELECT id, name, type, rating, unit 
            FROM device 
            ORDER BY type, name
        """)
        devices = cursor.fetchall()
        
        # Get usage data for the last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        cursor.execute("""
            SELECT du.device_id, d.name, d.type, d.rating, d.unit, 
                   du.date, du.hours_used,
                   (du.hours_used * d.rating) as total_usage
            FROM device_usage du
            JOIN device d ON du.device_id = d.id
            WHERE du.date >= %s
            ORDER BY du.date DESC, d.name
        """, (thirty_days_ago,))
        usage_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'devices': devices,
            'usage_data': usage_data
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        if conn:
            conn.close()
        return None

def analyze_usage_patterns(devices, usage_data):
    """Analyze usage patterns and create insights"""
    if not devices or not usage_data:
        return "No data available for analysis."
    
    # Group usage by device type
    electric_devices = []
    water_devices = []
    waste_devices = []
    
    for device in devices:
        device_id, name, device_type, rating, unit = device
        device_usage = [u for u in usage_data if u[0] == device_id]
        
        device_info = {
            'id': device_id,
            'name': name,
            'type': device_type,
            'rating': rating,
            'unit': unit,
            'usage_records': device_usage
        }
        
        if device_type == 'electric':
            electric_devices.append(device_info)
        elif device_type == 'water':
            water_devices.append(device_info)
        elif device_type == 'waste':
            waste_devices.append(device_info)
    
    # Calculate total usage by type
    total_electric_usage = sum(sum(u[7] for u in device['usage_records']) for device in electric_devices)
    total_water_usage = sum(sum(u[7] for u in device['usage_records']) for device in water_devices)
    total_waste_usage = sum(sum(u[7] for u in device['usage_records']) for device in waste_devices)
    
    # Find highest usage devices
    all_devices_with_total = []
    for device in electric_devices + water_devices + waste_devices:
        total_usage = sum(u[7] for u in device['usage_records'])
        all_devices_with_total.append((device, total_usage))
    
    highest_usage_devices = sorted(all_devices_with_total, key=lambda x: x[1], reverse=True)[:5]
    
    return {
        'electric_devices': electric_devices,
        'water_devices': water_devices,
        'waste_devices': waste_devices,
        'total_electric': total_electric_usage,
        'total_water': total_water_usage,
        'total_waste': total_waste_usage,
        'highest_usage': highest_usage_devices
    }

def generate_insights_prompt(analysis_data):
    """Generate a comprehensive prompt for Gemini API"""
    
    prompt = f"""
You are an energy and resource conservation expert. Analyze the following device usage data and provide actionable insights to help reduce resource consumption.

DEVICE INVENTORY:
"""
    
    # Add device information
    for device_type, devices in [('Electric', analysis_data['electric_devices']), 
                                ('Water', analysis_data['water_devices']), 
                                ('Waste', analysis_data['waste_devices'])]:
        if devices:
            prompt += f"\n{device_type} Devices:\n"
            for device in devices:
                total_usage = sum(u[7] for u in device['usage_records'])
                prompt += f"- {device['name']}: {device['rating']} {device['unit']} (Total usage: {total_usage:.2f})\n"
    
    prompt += f"""
USAGE SUMMARY (Last 30 days):
- Total Electric Usage: {analysis_data['total_electric']:.2f} kWh
- Total Water Usage: {analysis_data['total_water']:.2f} L
- Total Waste Production: {analysis_data['total_waste']:.2f} kg

HIGHEST USAGE DEVICES:
"""
    
    for device, total_usage in analysis_data['highest_usage']:
        prompt += f"- {device['name']}: {total_usage:.2f} {device['unit']}\n"
    
    prompt += """
Please provide:
1. **Energy Conservation Tips**: Specific recommendations for reducing electricity usage
2. **Water Saving Strategies**: Ways to reduce water consumption
3. **Waste Reduction Methods**: Tips for minimizing waste production
4. **Device-Specific Recommendations**: Targeted advice for the highest usage devices
5. **Behavioral Changes**: Simple lifestyle changes that can make a significant impact
6. **Cost Savings Estimates**: Potential monthly/yearly savings from implementing these changes and currency should be in Rupees

Format your response in a clear, actionable manner with specific, implementable recommendations.
"""
    
    return prompt

def get_gemini_insights():
    """Main function to get insights from Gemini API"""
    print("🔍 Fetching device data from database...")
    data = fetch_device_data()
    
    if not data:
        print("❌ Failed to fetch data from database")
        return None
    
    print(f"✅ Found {len(data['devices'])} devices and {len(data['usage_data'])} usage records")
    
    print("📊 Analyzing usage patterns...")
    analysis = analyze_usage_patterns(data['devices'], data['usage_data'])
    
    print("🤖 Generating insights with Gemini AI...")
    prompt = generate_insights_prompt(analysis)
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error getting insights from Gemini: {e}")
        return None

def main():
    """Main function to run the insights generator"""
    print("🌿 EcoBuddy Resource Insights Generator")
    print("=" * 50)
    
    insights = get_gemini_insights()
    
    if insights:
        print("\n" + "=" * 50)
        print("💡 RESOURCE CONSERVATION INSIGHTS")
        print("=" * 50)
        print(insights)
        print("=" * 50)
    else:
        print("❌ Failed to generate insights")

if __name__ == "__main__":
    main() 