#!/usr/bin/env python3
"""
Show information about the trained ML model
"""

import os
import json
import pickle
from datetime import datetime

def show_model_info():
    """Display information about the trained model"""
    print("🧠 Smart Traffic Control - ML Model Information")
    print("=" * 50)
    
    model_path = 'models/traffic_model.pkl'
    scaler_path = 'models/scaler.pkl'
    info_path = 'models/model_info.json'
    
    # Check if model files exist
    if not os.path.exists(model_path):
        print("❌ No trained model found!")
        print("💡 Run 'python run.py' to train and save a model")
        return
    
    # Show file information
    print("📁 Model Files:")
    for file_path, description in [
        (model_path, "Trained RandomForest model"),
        (scaler_path, "Feature scaler"),
        (info_path, "Model metadata")
    ]:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  ✅ {file_path}")
            print(f"     📊 Size: {size:,} bytes")
            print(f"     🕒 Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     📝 {description}")
        else:
            print(f"  ❌ {file_path} - Missing")
        print()
    
    # Load and display model information
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r') as f:
                info = json.load(f)
            
            print("🔍 Model Details:")
            print(f"  🤖 Type: {info.get('model_type', 'Unknown')}")
            print(f"  🌳 Trees: {info.get('n_estimators', 'Unknown')}")
            print(f"  📊 Features: {', '.join(info.get('features', []))}")
            print(f"  🎯 Trained: {info.get('trained_at', 'Unknown')}")
            print(f"  ✅ Status: {'Ready' if info.get('is_trained', False) else 'Not trained'}")
            
        except Exception as e:
            print(f"⚠️ Error reading model info: {e}")
    
    # Load and show model details
    try:
        print("\n🔬 Technical Details:")
        
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        print(f"  🌲 Estimators: {model.n_estimators}")
        print(f"  🎲 Random State: {model.random_state}")
        print(f"  📏 Max Depth: {model.max_depth}")
        print(f"  🍃 Min Samples Split: {model.min_samples_split}")
        
        # Load scaler
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        print(f"  📊 Scaler Type: {type(scaler).__name__}")
        if hasattr(scaler, 'mean_'):
            print(f"  📈 Feature Means: {scaler.mean_}")
            print(f"  📉 Feature Scales: {scaler.scale_}")
        
    except Exception as e:
        print(f"⚠️ Error loading model details: {e}")
    
    print("\n🚀 Usage:")
    print("  • Model is automatically loaded when system starts")
    print("  • Predictions are made using this trained model")
    print("  • Model is retrained and saved when system restarts")
    print("  • Use 'python run.py' to start the traffic system")

def main():
    show_model_info()

if __name__ == "__main__":
    main()