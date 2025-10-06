#!/usr/bin/env python3
"""
Smart Traffic Control System - Quick Start Script
This script provides an easy way to run the system
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Run setup first: python setup.py")
        return False

def start_application():
    """Start the Flask application"""
    print("🚦 Starting Smart Traffic Control System...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('models').mkdir(exist_ok=True)
    
    try:
        # Import and run the application
        from app import app, init_db, predictor
        
        # Initialize database
        print("🗄️ Initializing database...")
        init_db()
        
        # Train ML model
        print("🧠 Training ML model...")
        predictor.train_model()
        
        print("✅ System initialized successfully!")
        print("🌐 Starting web server...")
        print("📊 Dashboard will be available at: http://localhost:5000")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
                print("🌐 Browser opened automatically")
            except:
                print("⚠️ Could not open browser automatically")
                print("📱 Please open http://localhost:5000 manually")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the Flask application
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def show_help():
    """Show help information"""
    print("🚦 Smart Traffic Control System - Quick Start")
    print("=" * 50)
    print("Usage: python run.py [option]")
    print("")
    print("Options:")
    print("  start    Start the application (default)")
    print("  setup    Run initial setup")
    print("  test     Test system components")
    print("  help     Show this help message")
    print("")
    print("Quick Start:")
    print("1. python setup.py    # First time setup")
    print("2. python run.py      # Start the system")
    print("3. Open: http://localhost:5000")

def run_setup():
    """Run the setup script"""
    try:
        subprocess.run([sys.executable, 'setup.py'], check=True)
    except subprocess.CalledProcessError:
        print("❌ Setup failed")
        return False
    return True

def test_system():
    """Test system components"""
    print("🧪 Testing Smart Traffic Control System...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Dependencies
    print("1. Testing dependencies...")
    if check_dependencies():
        print("   ✅ All dependencies available")
        tests_passed += 1
    else:
        print("   ❌ Missing dependencies")
    
    # Test 2: Database
    print("2. Testing database...")
    try:
        import sqlite3
        conn = sqlite3.connect('traffic_data.db')
        conn.close()
        print("   ✅ Database connection successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
    
    # Test 3: ML Model
    print("3. Testing ML model...")
    try:
        from app import TrafficPredictor
        predictor = TrafficPredictor()
        predictor.train_model()
        prediction = predictor.predict(12, 1, 0)  # Test prediction
        print(f"   ✅ ML model working (sample prediction: {prediction})")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ ML model test failed: {e}")
    
    # Test 4: Web Application
    print("4. Testing web application...")
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/api/current-traffic')
            if response.status_code == 200:
                print("   ✅ Web application responding")
                tests_passed += 1
            else:
                print(f"   ❌ Web application error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Web application test failed: {e}")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! System is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = 'start'
    
    if command == 'setup':
        run_setup()
    elif command == 'test':
        test_system()
    elif command == 'help':
        show_help()
    elif command == 'start':
        start_application()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()