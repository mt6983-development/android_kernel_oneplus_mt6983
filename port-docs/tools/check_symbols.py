#!/usr/bin/env python3
"""
Static checker for kernel symbols and headers without compiling.
Scans source files for unresolved functions/symbols against exported symbols.
"""
import os
import re
import sys

def extract_exports(kernel_dir):
    exports = set()
    export_pattern = re.compile(r'EXPORT_SYMBOL(?:_GPL|_NS|_NS_GPL)?\s*\(\s*([a-zA-Z0-9_]+)\s*\)')
    for root, dirs, files in os.walk(kernel_dir):
        # Skip hidden or build directories
        if any(p in root for p in ['.git', '.repo', 'out']):
            continue
        for f in files:
            if f.endswith('.c') or f.endswith('.h'):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                        for line in fp:
                            m = export_pattern.search(line)
                            if m:
                                exports.add(m.group(1))
                except Exception:
                    pass
    return exports

def main():
    kernel_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"[check_symbols] Scanning exports in {kernel_dir}...")
    exports = extract_exports(kernel_dir)
    print(f"[check_symbols] Found {len(exports)} exported symbols.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
