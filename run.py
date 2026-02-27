import sys
import os
import uvicorn

if __name__ == "__main__":
    # 1. Force add current directory to Python Path
    # This solves issues when running from UNC paths or network shares
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print(f"Starting Server from: {current_dir}")
    print("API Documentation: http://localhost:8000/docs")
    
    # 2. Run Uvicorn Programmatically
    # reload=True might be tricky on UNC, setting to False for stability unless needed
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    except Exception as e:
        print(f"Failed to start server: {e}")
        input("Press Enter to exit...")
