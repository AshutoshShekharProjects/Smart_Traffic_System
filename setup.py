#!/usr/bin/env python3
"""
Smart Traffic Control System - Setup Script
Cross-platform setup for Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import platform
import sqlite3
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'models', 'data', 'static', 'templates', 'scripts']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

def initialize_database():
    """Initialize the SQLite database"""
    print("🗄️ Initializing database...")
    
    try:
        conn = sqlite3.connect('traffic_data.db')
        cursor = conn.cursor()
        
        # Create main traffic data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT,
                timestamp TEXT,
                vehicle_count INTEGER,
                avg_speed REAL,
                congestion_level TEXT,
                predicted_flow INTEGER
            )
        ''')
        
        # Create health reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                status TEXT,
                issues_count INTEGER,
                issues TEXT
            )
        ''')
        
        # Create future predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS future_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                hour INTEGER,
                predicted_flow INTEGER,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def setup_scheduling():
    """Setup scheduling based on the operating system"""
    system = platform.system().lower()
    
    if system == 'windows':
        setup_windows_scheduling()
    else:
        setup_unix_scheduling()

def setup_windows_scheduling():
    """Setup Windows Task Scheduler"""
    print("⏰ Setting up Windows Task Scheduler...")
    
    # Create batch files for Windows scheduling
    batch_files = {
        'data_collector.bat': 'cd /d "%~dp0" && python scripts/data_collector.py >> logs/cron.log 2>&1',
        'ml_predictor.bat': 'cd /d "%~dp0" && python scripts/ml_predictor.py >> logs/cron.log 2>&1',
        'health_check.bat': 'cd /d "%~dp0" && python scripts/health_check.py >> logs/cron.log 2>&1'
    }
    
    for filename, content in batch_files.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Created {filename}")
    
    print("📋 Windows Task Scheduler setup:")
    print("  1. Open Task Scheduler (taskschd.msc)")
    print("  2. Create Basic Task for each .bat file:")
    print("     - data_collector.bat: Every 5 minutes")
    print("     - ml_predictor.bat: Every 15 minutes") 
    print("     - health_check.bat: Every hour")
    print("  3. Set 'Start in' directory to project folder")

def setup_unix_scheduling():
    """Setup UNIX cron jobs"""
    print("⏰ Setting up UNIX cron jobs...")
    
    try:
        # Make scripts executable
        script_files = ['scripts/data_collector.py', 'scripts/ml_predictor.py', 'scripts/health_check.py']
        for script in script_files:
            if os.path.exists(script):
                os.chmod(script, 0o755)
        
        print("✅ Made scripts executable")
        print("📋 To setup cron jobs, run: bash scripts/setup_cron.sh")
        
    except Exception as e:
        print(f"⚠️ Could not make scripts executable: {e}")
        print("📋 Manually run: chmod +x scripts/*.py scripts/*.sh")

def test_system():
    """Test the system components"""
    print("🧪 Testing system components...")
    
    try:
        # Test imports
        import flask
        import pandas
        import numpy
        import sklearn
        print("✅ All required packages imported successfully")
        
        # Test database connection
        conn = sqlite3.connect('traffic_data.db')
        conn.close()
        print("✅ Database connection successful")
        
        # Test ML model training
        sys.path.append('.')
        from app import TrafficPredictor
        predictor = TrafficPredictor()
        predictor.train_model()
        print("✅ ML model training successful")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚦 Smart Traffic Control System - Setup")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return False
    
    # Initialize database
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        return False
    
    # Setup scheduling
    setup_scheduling()
    
    # Test system
    if not test_system():
        print("❌ Setup completed but system test failed")
        print("⚠️ Please check the error messages above")
    else:
        print("✅ Setup completed successfully!")
    
    print("\n🚀 Next Steps:")
    print("1. Run the application: python app.py")
    print("2. Open browser: http://localhost:5000")
    print("3. Check logs: tail -f logs/*.log (Unix) or type logs\\*.log (Windows)")
    print("4. For deployment: python deploy.py or ./deploy.sh")
    
    print("\n📚 Documentation:")
    print("- README.md: Project overview")
    print("- PRESENTATION.md: Presentation guide")
    print("- requirements.txt: Dependencies list")

if __name__ == "__main__":
    main()