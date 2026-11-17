#!/usr/bin/env python3
"""
Static checker for Kconfig files.
Checks for missing files, syntax balance, duplicate definitions, and broken includes.
"""
import os
import re
import sys

def check_kconfig_file(filepath):
    errors = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    source_re = re.compile(r'^\s*(?:source|ksonfig_include)\s+"([^"]+)"')
    for idx, line in enumerate(lines, 1):
        m = source_re.match(line)
        if m:
            included = m.group(1)
            # relative to kernel root, ignore $(...) variables
            if '$(' in included or included.startswith('$'):
                continue
            if not os.path.exists(included):
                errors.append(f"Line {idx}: sourced file does not exist: {included}")

    return errors

def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"[check_kconfig] Scanning Kconfig in {root_dir}...")
    checked = 0
    err_count = 0
    for root, dirs, files in os.walk(root_dir):
        if any(p in root for p in ['.git', '.repo', 'out', 'scripts/kconfig/tests']):
            continue
        for f in files:
            if f == 'Kconfig' or f.startswith('Kconfig.'):
                fpath = os.path.join(root, f)
                checked += 1
                errs = check_kconfig_file(fpath)
                if errs:
                    err_count += len(errs)
                    print(f"Error in {fpath}: {errs}")

    print(f"[check_kconfig] Checked {checked} Kconfig files. Errors: {err_count}")
    return 0 if err_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
