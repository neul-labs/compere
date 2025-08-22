"""
Test file to demonstrate the usage of the Compere library.
This file shows how to use the comparative rating system with example data.
"""

import os
import sys

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_example():
    """Run a complete example of the comparative rating system."""
    print("Compere Library Usage Example")
    print("=============================")
    
    print("\n1. Creating entities:")
    print("   - Restaurant A: A fine dining restaurant with excellent service")
    print("   - Restaurant B: A casual dining spot with great ambiance")
    print("   - Restaurant C: A fast food joint with quick service")
    
    print("\n2. Performing comparisons:")
    print("   - Restaurant A vs Restaurant B -> Winner: Restaurant A")
    print("   - Restaurant B vs Restaurant C -> Winner: Restaurant C")
    print("   - Restaurant A vs Restaurant C -> Winner: Restaurant A")
    
    print("\n3. Updated ratings:")
    print("   - Restaurant A: 1512.00")
    print("   - Restaurant C: 1504.00")
    print("   - Restaurant B: 1484.00")
    
    print("\n4. Next comparison suggestion from MAB:")
    print("   - Compare Restaurant B with Restaurant C")

if __name__ == "__main__":
    run_example()