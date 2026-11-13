"""
06_run_all.py
Master replication script.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_directories
from build_igi import build_igi_main
from real_data_analysis import real_data_main
from abm_simulation import abm_main
from abm_calibration import calibration_main
from sensitivity_analysis import sensitivity_main

def main():
    print("=" * 70)
    print("INFORMATION-GRANULARITY THEORY: FULL REPLICATION PIPELINE")
    print("=" * 70)
    
    setup_directories()
    
    print("\n[1/5] Building Information-Granularity Index...")
    build_igi_main()
    
    print("\n[2/5] Running real-data analysis...")
    real_data_main()
    
    print("\n[3/5] Running agent-based model...")
    abm_main()
    
    print("\n[4/5] Calibrating ABM to historical cases...")
    calibration_main()
    
    print("\n[5/5] Running sensitivity analysis...")
    sensitivity_main()
    
    print("\n" + "=" * 70)
    print("REPLICATION COMPLETE. SEE output/ DIRECTORY FOR RESULTS.")
    print("=" * 70)

if __name__ == '__main__':
    main()
