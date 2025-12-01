"""
Quick start script for running all services
Run from the backend directory
"""

import subprocess
import sys
import time
from pathlib import Path

def run_service(script_path, name, port):
    """Run a service in a new process"""
    print(f"\n{'='*60}")
    print(f"Starting {name} on port {port}...")
    print(f"{'='*60}\n")
    
    try:
        # Use the current Python interpreter from venv
        python_exe = sys.executable
        subprocess.Popen([python_exe, str(script_path)])
        print(f"✓ {name} started successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to start {name}: {e}")
        return False

def main():
    backend_dir = Path(__file__).parent
    
    print("""
╔══════════════════════════════════════════════════════════╗
║   ProActive Mobility Intelligence (PMI) - Startup       ║
║   Autonomous Predictive Maintenance System              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    services = [
        (backend_dir / "simulators" / "telemetry_simulator.py", "Telemetry Simulator", 8001),
        (backend_dir / "api" / "ingestion_service.py", "Ingestion Service", 8000),
        (backend_dir / "data" / "stream_consumer.py", "Stream Consumer", None),
    ]
    
    print("\nStarting services...")
    print("Note: Each service will open in the same terminal.")
    print("To run them separately, open 3 terminals and run each script individually.\n")
    
    for script, name, port in services:
        if not script.exists():
            print(f"✗ Script not found: {script}")
            continue
        
        port_info = f"port {port}" if port else "background process"
        print(f"\nTo start {name} ({port_info}):")
        print(f"  python {script.relative_to(backend_dir)}")
    
    print(f"\n{'='*60}")
    print("MANUAL START INSTRUCTIONS:")
    print(f"{'='*60}\n")
    print("Open 3 separate PowerShell terminals in the backend directory:\n")
    print("Terminal 1 (Simulator):")
    print("  cd simulators")
    print("  python telemetry_simulator.py\n")
    print("Terminal 2 (Ingestion):")
    print("  cd api")
    print("  python ingestion_service.py\n")
    print("Terminal 3 (Consumer):")
    print("  cd data")
    print("  python stream_consumer.py\n")
    print(f"{'='*60}")
    print("\nAfter starting, access:")
    print("  • Simulator API: http://localhost:8001/docs")
    print("  • Ingestion API: http://localhost:8000/docs")
    print("  • Grafana: http://localhost:3000 (admin/admin123)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
