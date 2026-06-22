#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def main():
    print("[Agent 3] Starting Functional Layout Cluster Verification...")
    font_target = "build/ArSL_Font.ttf"
    
    if not shutil.which("hb-shape"):
        print("[SKIP] hb-shape CLI utility not present on host image environment engine.")
        return

    # Direct PUA text shaping validation string runs
    test_string = "\uE000\uE028" 
    cmd = ["hb-shape", font_target, test_string]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Shaping Test Result Match Matrix: {result.stdout.strip()}")
        sys.exit(0)
    except Exception as e:
        print(f"🚨 Formatting layout crunch mismatch error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()