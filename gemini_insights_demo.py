import psycopg2
from datetime import datetime, timedelta

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

def generate_demo_insights(analysis_data):
    """Generate demo insights without requiring Gemini API"""
    
    insights = f"""
# 💡 Resource Conservation Insights

## 📊 Usage Summary (Last 30 days)
- **Total Electric Usage**: {analysis_data['total_electric']:.2f} kWh
- **Total Water Usage**: {analysis_data['total_water']:.2f} L
- **Total Waste Production**: {analysis_data['total_waste']:.2f} kg

## 🔍 Device Analysis

### Highest Usage Devices:
"""
    
    for i, (device, total_usage) in enumerate(analysis_data['highest_usage'], 1):
        insights += f"{i}. **{device['name']}**: {total_usage:.2f} {device['unit']}\n"
    
    insights += f"""
## 💡 Conservation Recommendations

### 1. Energy Conservation Tips:
- **Optimize Fan Usage**: Your fan is running {analysis_data['total_electric']:.2f} kWh. Consider using ceiling fans instead of portable fans for better efficiency
- **Smart Scheduling**: Use timers to automatically turn off devices when not needed
- **Energy-Efficient Alternatives**: Consider upgrading to energy-efficient models

### 2. Water Saving Strategies:
- **Fix Leaks**: Check for dripping taps and fix them immediately
- **Shorter Showers**: Reduce shower time by 2-3 minutes
- **Efficient Appliances**: Use water-efficient fixtures and appliances

### 3. Waste Reduction Methods:
- **Composting**: Start composting organic waste
- **Recycling**: Separate recyclables from general waste
- **Reduce Packaging**: Choose products with minimal packaging

### 4. Device-Specific Recommendations:
"""
    
    for device, total_usage in analysis_data['highest_usage'][:3]:
        if device['type'] == 'electric':
            insights += f"- **{device['name']}**: Consider using a smart plug to monitor and control usage\n"
        elif device['type'] == 'water':
            insights += f"- **{device['name']}**: Install a water-saving aerator\n"
        elif device['type'] == 'waste':
            insights += f"- **{device['name']}**: Implement a waste sorting system\n"
    
    insights += """
### 5. Behavioral Changes:
- **Turn off devices** when leaving the room
- **Use natural light** during the day
- **Batch tasks** to reduce device startup/shutdown cycles
- **Regular maintenance** to keep devices running efficiently

### 6. Estimated Savings:
- **Electricity**: 15-25% reduction possible with smart usage
- **Water**: 20-30% savings with conservation practices
- **Waste**: 40-50% reduction through recycling and composting

## 🎯 Next Steps:
1. Implement the highest-impact recommendations first
2. Monitor usage for 2 weeks to see improvements
3. Gradually adopt more conservation practices
4. Share these insights with family members for collective impact
"""
    
    return insights

def get_demo_insights():
    """Main function to get demo insights"""
    print("🔍 Fetching device data from database...")
    data = fetch_device_data()
    
    if not data:
        print("❌ Failed to fetch data from database")
        return None
    
    print(f"✅ Found {len(data['devices'])} devices and {len(data['usage_data'])} usage records")
    
    print("📊 Analyzing usage patterns...")
    analysis = analyze_usage_patterns(data['devices'], data['usage_data'])
    
    print("💡 Generating demo insights...")
    insights = generate_demo_insights(analysis)
    
    return insights

def main():
    """Main function to run the demo insights generator"""
    print("🌿 EcoBuddy Resource Insights Generator (Demo)")
    print("=" * 50)
    
    insights = get_demo_insights()
    
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