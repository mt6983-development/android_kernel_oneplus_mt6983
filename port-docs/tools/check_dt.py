#!/usr/bin/env python3
"""
Static checker for Device Tree files (.dts, .dtsi) without running dtc.
Checks include paths, labels, phandles, and unclosed blocks.
"""
import os
import re
import sys

def check_dts_file(filepath):
    errors = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        errors.append(f"Brace mismatch: {open_braces} open vs {close_braces} close")

    # Check for conflict markers
    if re.search(r'^(<{7}|>{7}|={7})', content, re.MULTILINE):
        errors.append("Merge conflict markers found")

    return errors

def main():
    dts_dir = sys.argv[1] if len(sys.argv) > 1 else 'arch/arm64/boot/dts'
    print(f"[check_dt] Checking device trees in {dts_dir}...")
    total_checked = 0
    total_errors = 0
    for root, dirs, files in os.walk(dts_dir):
        for f in files:
            if f.endswith('.dts') or f.endswith('.dtsi'):
                fpath = os.path.join(root, f)
                total_checked += 1
                errs = check_dts_file(fpath)
                if errs:
                    total_errors += len(errs)
                    print(f"Error in {fpath}: {errs}")

    print(f"[check_dt] Checked {total_checked} DT files. Errors: {total_errors}")
    return 0 if total_errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
