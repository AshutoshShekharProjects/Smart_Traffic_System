#!/usr/bin/env python3
"""
Restart Smart Traffic Control System with Indian Traffic Data
This script clears old data and restarts with Delhi & Bengaluru intersections
"""

import os
import sqlite3
import sys

def clear_old_data():
    """Clear old NYC data and prepare for Indian traffic data"""
    try:
        # Remove old database
        if os.path.exists('traffic_data.db'):
            os.remove('traffic_data.db')
            print("✅ Cleared old traffic database")
        
        # Remove old model files
        if os.path.exists('models/traffic_model.pkl'):
            os.remove('models/traffic_model.pkl')
            print("✅ Cleared old ML model")
            
        if os.path.exists('models/scaler.pkl'):
            os.remove('models/scaler.pkl')
            print("✅ Cleared old scaler model")
        
        print("🇮🇳 Ready to start with Indian traffic data!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing old data: {e}")
        return False

def main():
    print("🚦 Restarting Smart Traffic Control System")
    print("🇮🇳 Switching to Delhi & Bengaluru Traffic Data")
    print("=" * 50)
    
    if clear_old_data():
        print("\n🚀 Starting system with Indian traffic patterns...")
        print("📍 Monitoring 12 intersections across 4 cities:")
        print("   Delhi NCR:")
        print("   • Connaught Place (HIGH)")
        print("   • IFFCO Chowk, Gurgaon (HIGH)") 
        print("   • Lajpat Nagar (MEDIUM)")
        print("   • Dwarka Sector 21 (LOW)")
        print("   Bengaluru:")
        print("   • Silk Board Junction (HIGH)")
        print("   • Electronic City (HIGH)")
        print("   • Jayanagar 4th Block (MEDIUM)")
        print("   • Hebbal Flyover (LOW)")
        print("   Mumbai:")
        print("   • Bandra Kurla Complex (HIGH)")
        print("   • Andheri East (MEDIUM)")
        print("   Chennai:")
        print("   • Adyar Signal (MEDIUM)")
        print("   • OMR IT Corridor (LOW)")
        print("\n🔄 Enhanced Features:")
        print("   • Mixed congestion levels (High/Medium/Low)")
        print("   • City-specific traffic multipliers (Mumbai 1.4x, Delhi/Blr 1.2x)")
        print("   • Extended rush hours (7-11 AM, 4-9 PM)")
        print("   • Congestion-based speed calculations")
        print("   • Realistic traffic diversity across Indian cities")
        print("\n▶️  Run: python run.py")
    else:
        print("❌ Failed to clear old data")
        sys.exit(1)

if __name__ == "__main__":
    main()