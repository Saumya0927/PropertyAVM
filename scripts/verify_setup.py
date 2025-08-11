#!/usr/bin/env python3
"""
Verification script to check if all components are properly set up
"""

import sys
import os
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_python_imports():
    """Check if Python modules can be imported"""
    print("\n📦 Checking Python imports...")
    
    try:
        # Add backend to path
        sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
        
        # Try importing critical modules
        imports_to_check = [
            ('services.database', 'Database service'),
            ('services.redis_client', 'Redis client'),
            ('services.ml_service', 'ML service'),
            ('services.websocket_manager', 'WebSocket manager'),
            ('api.valuations', 'Valuations API'),
            ('api.auth', 'Auth API'),
            ('middleware.logging', 'Logging middleware'),
            ('middleware.metrics', 'Metrics middleware'),
        ]
        
        all_good = True
        for module_name, description in imports_to_check:
            try:
                __import__(module_name)
                print(f"  ✅ {description} ({module_name})")
            except ImportError as e:
                print(f"  ❌ {description} ({module_name}): {e}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"  ❌ Error checking imports: {e}")
        return False

def check_frontend_structure():
    """Check if frontend files are properly structured"""
    print("\n🎨 Checking frontend structure...")
    
    base_path = Path(__file__).parent.parent / 'frontend'
    
    required_files = [
        ('package.json', 'Package configuration'),
        ('next.config.js', 'Next.js configuration'),
        ('tsconfig.json', 'TypeScript configuration'),
        ('tailwind.config.js', 'Tailwind CSS configuration'),
        ('app/layout.tsx', 'Root layout'),
        ('app/page.tsx', 'Homepage'),
        ('app/valuation/page.tsx', 'Valuation page'),
        ('app/dashboard/page.tsx', 'Dashboard page'),
        ('components/Header.tsx', 'Header component'),
        ('components/Footer.tsx', 'Footer component'),
        ('components/ValuationForm.tsx', 'Valuation form'),
    ]
    
    all_good = True
    for filepath, description in required_files:
        full_path = base_path / filepath
        if full_path.exists():
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_good = False
    
    return all_good

def check_docker_config():
    """Check Docker configuration"""
    print("\n🐳 Checking Docker configuration...")
    
    base_path = Path(__file__).parent.parent
    
    docker_files = [
        ('docker-compose.yml', 'Docker Compose configuration'),
        ('backend/Dockerfile', 'Backend Dockerfile'),
        ('frontend/Dockerfile', 'Frontend Dockerfile'),
    ]
    
    all_good = True
    for filepath, description in docker_files:
        full_path = base_path / filepath
        if full_path.exists():
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_good = False
    
    return all_good

def check_ml_pipeline():
    """Check ML pipeline files"""
    print("\n🤖 Checking ML pipeline...")
    
    base_path = Path(__file__).parent.parent
    
    ml_files = [
        ('ml-pipeline/train_ensemble.py', 'Training script'),
        ('data-generator/generate_synthetic_data.py', 'Data generator'),
        ('lambda-functions/valuation_handler.py', 'Lambda function'),
    ]
    
    all_good = True
    for filepath, description in ml_files:
        full_path = base_path / filepath
        if full_path.exists():
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_good = False
    
    return all_good

def main():
    """Main verification function"""
    print("=" * 60)
    print("🔍 Property Valuation Model - Setup Verification")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(check_python_imports())
    results.append(check_frontend_structure())
    results.append(check_docker_config())
    results.append(check_ml_pipeline())
    
    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! The system is ready to run.")
        print("\n📋 Next steps:")
        print("  1. Run: cd data-generator && python generate_synthetic_data.py")
        print("  2. Run: cd ml-pipeline && python train_ensemble.py")
        print("  3. Run: docker-compose up -d")
        print("  4. Access: http://localhost:3000")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("\n📋 To fix:")
        print("  1. Install missing Python packages: pip install -r backend/requirements.txt")
        print("  2. Install frontend dependencies: cd frontend && npm install")
        print("  3. Review any missing files and create them")
    
    print("=" * 60)
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())