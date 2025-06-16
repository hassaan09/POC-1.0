#!/usr/bin/env python3
"""
Setup script for GUI Automation System
Handles installation and configuration
"""

import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    
    print("📦 Installing system dependencies...")
    
    if system == "windows":
        print("🪟 Windows detected")
        print("Please ensure you have:")
        print("  - Microsoft Visual C++ Build Tools")
        print("  - Windows SDK")
        print("  - Git (for some packages)")
        
    elif system == "linux":
        print("🐧 Linux detected")
        try:
            # Ubuntu/Debian
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True)
            
            subprocess.run([
                "sudo", "apt-get", "install", "-y",
                "python3-dev",
                "portaudio19-dev",
                "espeak",
                "espeak-data",
                "libespeak1",
                "libespeak-dev",
                "ffmpeg",
                "libsm6",
                "libxext6",
                "libxrender-dev",
                "libglib2.0-0"
            ], check=True)
            
            print("✅ System dependencies installed")
            
        except subprocess.CalledProcessError:
            print("❌ Failed to install system dependencies")
            print("Please install manually:")
            print("  sudo apt-get update")
            print("  sudo apt-get install python3-dev portaudio19-dev espeak ffmpeg")
            
    elif system == "darwin":
        print("🍎 macOS detected")
        try:
            # Check if Homebrew is installed
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            
            subprocess.run([
                "brew", "install",
                "portaudio",
                "espeak",
                "ffmpeg"
            ], check=True)
            
            print("✅ System dependencies installed")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Homebrew not found or failed to install dependencies")
            print("Please install Homebrew first: https://brew.sh/")
            print("Then run: brew install portaudio espeak ffmpeg")

def install_python_packages():
    """Install Python packages with error handling"""
    print("📦 Installing Python packages...")
    
    # Packages that might need special handling
    special_packages = {
        'pyaudio': 'PyAudio (audio processing)',
        'opencv-python': 'OpenCV (computer vision)',
        'torch': 'PyTorch (machine learning)'
    }
    
    try:
        # First, upgrade pip
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        # Install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ All Python packages installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install some packages: {e}")
        
        # Try installing packages individually
        print("🔄 Attempting individual package installation...")
        
        with open("requirements.txt", "r") as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        failed_packages = []
        
        for package in packages:
            try:
                print(f"Installing {package}...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True, capture_output=True)
                print(f"✅ {package}")
                
            except subprocess.CalledProcessError:
                print(f"❌ {package}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
            print("\nTry installing these manually:")
            for pkg in failed_packages:
                if any(special in pkg for special in special_packages):
                    print(f"  pip install {pkg} --user")
                else:
                    print(f"  pip install {pkg}")
            return False
        
        return True

def setup_configuration():
    """Setup application configuration"""
    print("⚙️ Setting up configuration...")
    
    # Create necessary directories
    directories = [
        "data",
        "data/logs",
        "data/screenshots", 
        "data/demos",
        "data/extracted_steps"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {directory}")
    
    print("✅ Configuration complete")

def run_tests():
    """Run basic functionality tests"""
    print("🧪 Running basic tests...")
    
    try:
        # Test imports
        print("Testing imports...")
        
        import gradio
        print(f"✅ Gradio {gradio.__version__}")
        
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
        
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
        
        import selenium
        print(f"✅ Selenium {selenium.__version__}")
        
        try:
            import speech_recognition
            print(f"✅ SpeechRecognition {speech_recognition.__version__}")
        except AttributeError:
            print("✅ SpeechRecognition (version not available)")
        
        import sklearn
        print(f"✅ Scikit-learn {sklearn.__version__}")
        
        # Test system functionality
        print("\nTesting system functionality...")
        
        import pyautogui
        size = pyautogui.size()
        print(f"✅ Screen automation ready (Screen: {size.width}x{size.height})")
        
        print("✅ All tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 GUI Automation System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python packages
    if not install_python_packages():
        print("\n❌ Setup incomplete due to package installation failures")
        print("Please resolve the issues above and run setup.py again")
        sys.exit(1)
    
    # Setup configuration
    setup_configuration()
    
    # Run tests
    if not run_tests():
        print("\n⚠️ Setup completed but some tests failed")
        print("The application might still work, but some features may be unavailable")
    else:
        print("\n🎉 Setup completed successfully!")
        print("\nTo start the application, run:")
        print("  python main.py")
        print("\nThe web interface will be available at:")
        print("  http://localhost:7860")

if __name__ == "__main__":
    main()