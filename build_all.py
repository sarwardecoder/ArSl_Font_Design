#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_step(step_name, command_args):
    print(f"\n🚀 [ORCHESTRATOR] Launching Subroutine: {step_name}...")
    try:
        subprocess.run(command_args, check=True)
        print(f"✅ {step_name} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {step_name} failed with exit code {e.returncode}!")
        return False

def main():
    print("=" * 64)
    print("      ARABIC SIGN LANGUAGE FONT SYSTEM — MASTER ORCHESTRATOR      ")
    print("=" * 64)

    ufo_dir = Path("source/ArSL_Base_Shell.ufo")
    build_dir = Path("build")

    # Clean workspace
    if ufo_dir.exists(): shutil.rmtree(ufo_dir)
    if build_dir.exists(): shutil.rmtree(build_dir)
    ufo_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Orchestrate sub-agent pipeline scripts sequentially
    if not run_step("Agent 2 (A): Component Layer Initializer", [sys.executable, "tools/create_component_layers.py"]): sys.exit(1)
    if not run_step("Agent 2 (B): Expression Markers Injection", [sys.executable, "tools/inject_expression_markers.py"]): sys.exit(1)
    if not run_step("Agent 2 (C): Expansion Slots Reservation", [sys.executable, "tools/inject_reserved_slots.py"]): sys.exit(1)

    # Agent 3 Compilation Phase
    compile_cmd = ["fontmake", "-u", str(ufo_dir), "-o", "ttf", "--keep-overlaps", "--no-autohint", "--output-path", "build/ArSL_Font.ttf"]
    if not run_step("Agent 3 (A): Fontmake Binary Compiler", compile_cmd): sys.exit(1)
    
    # Agent 3 Layout Phase
    if not run_step("Agent 3 (B): Text Shaping Verification", [sys.executable, "tools/test_shaping.py"]): sys.exit(1)

    print("\n" + "=" * 64)
    print("🎉 SUCCESS: Entire ArSL Font System recreated seamlessly!")
    print("=" * 64)

if __name__ == "__main__":
    main()