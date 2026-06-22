#!/usr/bin/env python3
"""
build_all.py
ArSL Font Project — Unified Lifecycle Orchestrator

Coordinates Agent 1, Agent 2, and Agent 3 subroutines into a single, fully 
automated execution loop to scaffold, inject, compile, and verify the font from scratch.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_step(step_name, command_args):
    """Executes a sub-agent process and manages logging output streams cleanly."""
    print(f"\n🚀 [ORCHESTRATOR] Launching Subroutine: {step_name}...")
    print(f"👉 Running: {' '.join(command_args)}")
    
    try:
        result = subprocess.run(command_args, capture_output=False, check=True)
        print(f"✅ {step_name} finished successfully.\n" + "-"*60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {step_name} failed with exit code {e.returncode}!")
        return False

def main():
    print("=" * 64)
    print("      ARABIC SIGN LANGUAGE FONT SYSTEM — MASTER ORCHESTRATOR      ")
    print("=" * 64)

    # Setup core path definitions
    ufo_dir = Path("source/ArSL_Base_Shell.ufo")
    build_dir = Path("build")

    # --- PHASE 0: Fresh Workspace Sanitation ---
    print("\n[PHASE 0] Sanitizing workspace targets...")
    if ufo_dir.exists():
        shutil.rmtree(ufo_dir)
        print("  Cleaned existing UFO source directories.")
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("  Cleaned existing distribution build artifacts.")
        
    # Recreate baseline directories
    ufo_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    # --- PHASE 1: Agent 1 (Schema & Database Infrastructure) ---
    # Scaffolds baseline configuration metadata and database constraints
    # (If you have generate_ufo.py or a database schema generator script)
    if os.path.exists("generate_ufo.py"):
        if not run_step("Agent 1: Schema Baseline Configuration Injection", [sys.executable, "generate_ufo.py"]):
            sys.exit(1)

    # --- PHASE 2: Agent 2 (OpenType Component Geometry Processing Layers) ---
    # Step A: Setup core hand component structures across slots 1-28
    if not run_step("Agent 2 (Step A): Layering Hand Shape Structures", [sys.executable, "tools/create_component_layers.py"]):
        sys.exit(1)

    # Step B: Setup expression overlay matrices across slots 41-45
    if not run_step("Agent 2 (Step B): Injecting Facial Expression Markers", [sys.executable, "tools/inject_expression_markers.py"]):
        sys.exit(1)

    # Step C: Setup final expansion slot layout maps across slots 46-60
    if not run_step("Agent 2 (Step C): Locking Down Reserved Dialect Allocations", [sys.executable, "tools/inject_reserved_slots.py"]):
        sys.exit(1)

    # --- PHASE 3: Agent 3 (Compilation and QA Verification Framework) ---
    # Step A: Compile binary font production outputs
    compile_cmd = [
        "fontmake", "-u", str(ufo_dir), "-o", "ttf", 
        "--keep-overlaps", "--no-autohint", "--output-path", "build/ArSL_Font.ttf"
    ]
    if not run_step("Agent 3 (Step A): Running Production Binary Compiler", compile_cmd):
        sys.exit(1)

    # Step B: Run text-shaping cluster tests via HarfBuzz metrics
    if not run_step("Agent 3 (Step B): Executing Text Shaping Validation Suite", [sys.executable, "tools/test_shaping.py"]):
        sys.exit(1)

    print("\n" + "=" * 64)
    print("🎉 SUCCESS: Entire ArSL Font System recreated seamlessly!")
    print(f"   Outputs archived inside target path: {build_dir.resolve()}")
    print("=" * 64)

if __name__ == "__main__":
    main()