#!/usr/bin/env python3
"""
P3E Release Package Creator

Creates organized release packages from test artifacts to support General Atomics 
findings of cell runaway/high delta voltage issues. Each release package contains:
- CSV files showing cell runaway data
- JSON metadata files
- Dashboard screenshots showing cell delta plots

Usage:
    python P3E-Report/create_release_package.py [serial_number]
    python P3E-Report/create_release_package.py --all
    python P3E-Report/create_release_package.py --list-serials
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

class P3EReleasePackager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.test_artifacts_dir = self.base_dir / "test-artifacts"
        self.release_dir = self.base_dir / "release"
        self.rma_status_file = self.base_dir / "rma-pack-status.json"
        
    def load_rma_status(self):
        """Load RMA pack status to identify failed packs"""
        try:
            with open(self.rma_status_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.rma_status_file} not found")
            return {}
    
    def get_serial_numbers(self):
        """Get list of available serial numbers from test artifacts"""
        if not self.test_artifacts_dir.exists():
            return []
        
        serials = []
        for item in self.test_artifacts_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                serials.append(item.name)
        return sorted(serials)
    
    def has_failure_evidence(self, serial_number, rma_status):
        """Check if serial number has evidence of failures"""
        ga_data = rma_status.get("test_results", {}).get("general_atomics", {}).get(serial_number, {})
        
        charge_failed = ga_data.get("charge", {}).get("status") == "failed"
        discharge_failed = ga_data.get("discharge", {}).get("status") == "failed"
        
        return charge_failed or discharge_failed
    
    def find_best_evidence_files(self, serial_dir):
        """Find CSV/JSON files that best demonstrate cell runaway"""
        evidence_files = {"charge": [], "discharge": []}
        
        for test_type in ["charge", "discharge"]:
            test_dir = serial_dir / test_type
            if test_dir.exists():
                csv_files = list(test_dir.glob("*.csv"))
                json_files = list(test_dir.glob("*.json"))
                
                # Pair CSV and JSON files
                for csv_file in csv_files:
                    json_file = csv_file.with_suffix('.json')
                    if json_file.exists():
                        evidence_files[test_type].append({
                            "csv": csv_file,
                            "json": json_file,
                            "timestamp": csv_file.stem.split('-')[0]
                        })
                
                # Sort by timestamp and take the latest
                evidence_files[test_type].sort(key=lambda x: x["timestamp"], reverse=True)
        
        return evidence_files
    
    def create_dashboard_screenshot(self, csv_file, output_path, test_type):
        """Create dashboard screenshot for the CSV file"""
        try:
            # Use the dashboard to create screenshot
            dashboard_cmd = [
                sys.executable, "-m", "src.modbus_dashboard",
                "--historical", str(csv_file),
                "--session-type", test_type,
                "--export-screenshot", str(output_path),
                "--no-gui"  # Run headless if possible
            ]
            
            print(f"Creating screenshot for {csv_file.name}...")
            result = subprocess.run(dashboard_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✓ Screenshot saved: {output_path}")
                return True
            else:
                print(f"✗ Screenshot failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ Screenshot timeout for {csv_file.name}")
            return False
        except Exception as e:
            print(f"✗ Screenshot error: {e}")
            return False
    
    def create_release_package(self, serial_number):
        """Create release package for a specific serial number"""
        print(f"\nCreating release package for serial {serial_number}...")
        
        # Check if we have test artifacts for this serial
        serial_artifacts_dir = self.test_artifacts_dir / serial_number
        if not serial_artifacts_dir.exists():
            print(f"✗ No test artifacts found for serial {serial_number}")
            return False
        
        # Create release directory structure
        release_serial_dir = self.release_dir / serial_number
        release_serial_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for subdir in ["charge", "discharge", "screenshots"]:
            (release_serial_dir / subdir).mkdir(exist_ok=True)
        
        # Find best evidence files
        evidence_files = self.find_best_evidence_files(serial_artifacts_dir)
        
        copied_files = []
        screenshots_created = []
        
        # Process charge and discharge evidence
        for test_type, files in evidence_files.items():
            if files:
                # Take the best evidence file (latest timestamp)
                best_file = files[0]
                
                # Copy CSV and JSON to release directory
                dest_csv = release_serial_dir / test_type / best_file["csv"].name
                dest_json = release_serial_dir / test_type / best_file["json"].name
                
                shutil.copy2(best_file["csv"], dest_csv)
                shutil.copy2(best_file["json"], dest_json)
                
                copied_files.extend([dest_csv, dest_json])
                print(f"✓ Copied {test_type} evidence: {best_file['csv'].name}")
                
                # Create dashboard screenshot
                screenshot_name = f"sn-{serial_number}-{test_type}-cell-delta.png"
                screenshot_path = release_serial_dir / "screenshots" / screenshot_name
                
                if self.create_dashboard_screenshot(best_file["csv"], screenshot_path, test_type):
                    screenshots_created.append(screenshot_path)
        
        # Copy existing screenshots if available
        existing_screenshots_dir = serial_artifacts_dir / "screenshots"
        if existing_screenshots_dir.exists():
            for screenshot in existing_screenshots_dir.glob("*.png"):
                dest_screenshot = release_serial_dir / "screenshots" / f"original-{screenshot.name}"
                shutil.copy2(screenshot, dest_screenshot)
                print(f"✓ Copied existing screenshot: {screenshot.name}")
        
        # Create release summary
        self.create_release_summary(serial_number, copied_files, screenshots_created)
        
        print(f"✓ Release package created: {release_serial_dir}")
        return True
    
    def create_release_summary(self, serial_number, copied_files, screenshots):
        """Create a summary file for the release package"""
        release_serial_dir = self.release_dir / serial_number
        summary_file = release_serial_dir / "release_summary.json"
        
        rma_status = self.load_rma_status()
        ga_data = rma_status.get("test_results", {}).get("general_atomics", {}).get(serial_number, {})
        
        summary = {
            "serial_number": serial_number,
            "created": datetime.now().isoformat(),
            "purpose": "Cell runaway/high delta voltage evidence package",
            "ga_findings": ga_data,
            "included_files": {
                "csv_json_pairs": [str(f.relative_to(release_serial_dir)) for f in copied_files],
                "screenshots": [str(f.relative_to(release_serial_dir)) for f in screenshots]
            },
            "notes": "Package contains CSV data and dashboard screenshots supporting GA findings of cell voltage runaway issues"
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Release summary created: release_summary.json")
    
    def create_all_packages(self):
        """Create release packages for all serials with failure evidence"""
        rma_status = self.load_rma_status()
        serials = self.get_serial_numbers()
        
        if not serials:
            print("No serial numbers found in test artifacts")
            return
        
        print(f"Found {len(serials)} serial numbers: {', '.join(serials)}")
        
        created_count = 0
        for serial in serials:
            if self.has_failure_evidence(serial, rma_status):
                if self.create_release_package(serial):
                    created_count += 1
            else:
                print(f"Skipping {serial} - no failure evidence in RMA status")
        
        print(f"\n✓ Created {created_count} release packages")
    
    def list_serials(self):
        """List available serial numbers and their status"""
        rma_status = self.load_rma_status()
        serials = self.get_serial_numbers()
        
        if not serials:
            print("No serial numbers found in test artifacts")
            return
        
        print("Available Serial Numbers:")
        print("-" * 50)
        
        for serial in serials:
            ga_data = rma_status.get("test_results", {}).get("general_atomics", {}).get(serial, {})
            charge_status = ga_data.get("charge", {}).get("status", "unknown")
            discharge_status = ga_data.get("discharge", {}).get("status", "unknown")
            
            has_evidence = self.has_failure_evidence(serial, rma_status)
            evidence_marker = "📊" if has_evidence else "  "
            
            print(f"{evidence_marker} {serial}: Charge={charge_status}, Discharge={discharge_status}")

def main():
    parser = argparse.ArgumentParser(description="Create P3E release packages")
    parser.add_argument("serial_number", nargs="?", help="Specific serial number to package")
    parser.add_argument("--all", action="store_true", help="Create packages for all serials with failures")
    parser.add_argument("--list-serials", action="store_true", help="List available serial numbers")
    
    args = parser.parse_args()
    
    packager = P3EReleasePackager()
    
    if args.list_serials:
        packager.list_serials()
    elif args.all:
        packager.create_all_packages()
    elif args.serial_number:
        packager.create_release_package(args.serial_number)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()