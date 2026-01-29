import argparse
import glob
import os
import subprocess
from pathlib import Path

DEFAULT_ASEPRITE_PATHS = [
    r'D:\\tools\\Aseprite-v1.3.15.3-Windows\\aseprite.exe',
    r'C:\\Program Files\\Aseprite\\aseprite.exe',
    r'C:\\Program Files (x86)\\Aseprite\\aseprite.exe',
]


def find_aseprite(explicit):
    if explicit:
        p = Path(explicit)
        if p.exists():
            return str(p)
        raise SystemExit(f'Aseprite not found at: {explicit}')

    env = os.environ.get('ASEPRITE_EXE')
    if env and Path(env).exists():
        return env

    for p in DEFAULT_ASEPRITE_PATHS:
        if Path(p).exists():
            return p

    return 'aseprite.exe'


def expand_inputs(inputs):
    results = []
    for raw in inputs:
        matches = glob.glob(raw)
        if matches:
            for m in matches:
                p = Path(m)
                if p.is_dir():
                    results.extend(p.glob('*.aseprite'))
                else:
                    results.append(p)
            continue
        p = Path(raw)
        if p.is_dir():
            results.extend(p.glob('*.aseprite'))
        elif p.exists():
            results.append(p)
    unique = {}
    for p in results:
        unique[p.resolve()] = p
    return sorted(unique.values(), key=lambda x: str(x))


def export_file(aseprite, src, out_root, preview=False):
    base = src.stem
    target_root = Path(out_root) / base
    target_root.mkdir(parents=True, exist_ok=True)
    save_as = str(target_root / '{tag}' / '{frame}.png')
    cmd = [
        aseprite,
        '-b',
        str(src),
        '--split-tags',
        '--save-as',
        save_as,
    ]
    if preview:
        cmd.append('--preview')
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description='Extract per-tag frames from .aseprite files.')
    parser.add_argument('paths', nargs='+', help='Files, folders, or globs to scan')
    parser.add_argument('--aseprite', help='Path to aseprite.exe (or set ASEPRITE_EXE env var)')
    parser.add_argument('--output', default='assets', help='Output directory (default: assets)')
    parser.add_argument('--preview', action='store_true', help='Use Aseprite preview mode (no files written)')
    args = parser.parse_args()

    aseprite = find_aseprite(args.aseprite)
    files = expand_inputs(args.paths)
    if not files:
        raise SystemExit('No .aseprite files found for given inputs.')

    for f in files:
        export_file(aseprite, f, args.output, preview=args.preview)


if __name__ == '__main__':
    main()
