#!/usr/bin/env python3
"""
Check CSV file format to debug dashboard issues
"""

import sys
import csv
from pathlib import Path

def check_csv_file(filename):
    """Check the format of a CSV file"""
    file_path = Path(filename)
    
    if not file_path.exists():
        print(f"Error: File not found: {filename}")
        return
    
    print(f"Checking CSV file: {filename}")
    print("=" * 60)
    
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        
        # Read header
        try:
            header = next(reader)
            print(f"Header columns ({len(header)}):")
            for i, col in enumerate(header):
                print(f"  [{i}] {col}")
        except StopIteration:
            print("Error: Empty CSV file")
            return
        
        print("\nFirst 5 data rows:")
        print("-" * 60)
        
        row_count = 0
        for row in reader:
            if row_count < 5:
                print(f"Row {row_count + 1}:")
                if len(row) > 0:
                    print(f"  Timestamp: {row[0]}")
                if len(row) > 1:
                    print(f"  First cell voltage: {row[1]}")
                if len(row) > 18:
                    print(f"  Pack voltage: {row[18]}")
                print()
            row_count += 1
        
        print(f"Total data rows: {row_count}")

def find_latest_csv(directory, serial_number=None, rma_number=None):
    """Find the latest CSV file in directory"""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Error: Directory not found: {directory}")
        return None
    
    if serial_number and rma_number:
        pattern = f"*-{serial_number}-{rma_number}.csv"
        csv_files = list(dir_path.glob(pattern))
    else:
        csv_files = list(dir_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {directory}")
        if serial_number and rma_number:
            print(f"  Pattern: {pattern}")
        return None
    
    # Return most recent file
    latest = max(csv_files, key=lambda f: f.stat().st_mtime)
    print(f"Found latest CSV: {latest.name}")
    return latest

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_csv_format.py <csv_file>")
        print("  python check_csv_format.py --dir <directory> [--sn <serial>] [--rma <rma>]")
        return
    
    if sys.argv[1] == "--dir" and len(sys.argv) >= 3:
        directory = sys.argv[2]
        serial_number = None
        rma_number = None
        
        # Parse optional arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--sn" and i + 1 < len(sys.argv):
                serial_number = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--rma" and i + 1 < len(sys.argv):
                rma_number = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        csv_file = find_latest_csv(directory, serial_number, rma_number)
        if csv_file:
            check_csv_file(csv_file)
    else:
        check_csv_file(sys.argv[1])

if __name__ == "__main__":
    main()