import argparse
import glob
import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_ASEPRITE_PATHS = [
    r'D:\\tools\\Aseprite-v1.3.15.3-Windows\\aseprite.exe',
    r'C:\\Program Files\\Aseprite\\aseprite.exe',
    r'C:\\Program Files (x86)\\Aseprite\\aseprite.exe',
]
DEFAULT_SHADOW_LAYERS = ['shadow']


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


def list_layers(aseprite, src):
    cmd = [aseprite, '--batch', '--list-layers', str(src)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def resolve_shadow_layers(requested_layers, available_layers):
    available_lookup = {name.lower(): name for name in available_layers}
    resolved = []
    for layer_name in requested_layers:
        key = layer_name.lower()
        if key in available_lookup and available_lookup[key] not in resolved:
            resolved.append(available_lookup[key])
    return resolved


def find_nested_git_dir(target_root):
    if not target_root.exists():
        return None
    if target_root.name == '.git' and target_root.is_dir():
        return target_root
    for candidate in target_root.rglob('.git'):
        if candidate.is_dir():
            return candidate
    return None


def clean_target_directory(target_root, preview):
    if preview:
        print(f'[PREVIEW] Skip deleting target directory: {target_root}')
        return
    if not target_root.exists():
        print(f'[INFO] Target directory not found, skip clean: {target_root}')
        return
    git_dir = find_nested_git_dir(target_root)
    if git_dir is not None:
        raise SystemExit(f'Refusing to delete directory containing .git: {git_dir}')
    shutil.rmtree(target_root)
    print(f'[INFO] Removed target directory: {target_root}')


def build_export_cmd(aseprite, src, save_as, include_layers, ignore_layers, preview):
    cmd = [aseprite, '-b', '--split-tags']
    for layer_name in include_layers:
        cmd.extend(['--layer', layer_name])
    for layer_name in ignore_layers:
        cmd.extend(['--ignore-layer', layer_name])
    cmd.extend([str(src), '--save-as', save_as])
    if preview:
        cmd.append('--preview')
    return cmd


def run_export_command(cmd):
    printable = ' '.join([f'"{part}"' if ' ' in part else part for part in cmd])
    print(f'[RUN] {printable}')
    subprocess.run(cmd, check=True)


def export_file(
    aseprite,
    src,
    out_root,
    preview=False,
    split_shadow=False,
    shadow_layers=None,
    shadow_out_root='assets_shadow',
    clean_target=False,
    clean_shadow_target=False,
    strict_shadow_layer=True,
):
    base = src.stem
    main_target_root = Path(out_root) / base
    shadow_target_root = Path(shadow_out_root) / base

    if clean_target:
        clean_target_directory(main_target_root, preview)
    if split_shadow and clean_shadow_target:
        clean_target_directory(shadow_target_root, preview)

    active_shadow_layers = []
    if split_shadow:
        available_layers = list_layers(aseprite, src)
        active_shadow_layers = resolve_shadow_layers(shadow_layers, available_layers)
        print(f'[INFO] Sprite: {src}')
        print(f'[INFO] Available layers: {", ".join(available_layers) if available_layers else "<none>"}')
        print(f'[INFO] Requested shadow layers: {", ".join(shadow_layers)}')
        print(f'[INFO] Matched shadow layers: {", ".join(active_shadow_layers) if active_shadow_layers else "<none>"}')
        if not active_shadow_layers:
            error_message = (
                f'No shadow layer matched for {src}. '
                f'Requested={shadow_layers}, Available={available_layers}'
            )
            if strict_shadow_layer:
                raise SystemExit(error_message)
            print(f'[WARN] {error_message}')

    if not preview:
        main_target_root.mkdir(parents=True, exist_ok=True)
        if split_shadow:
            shadow_target_root.mkdir(parents=True, exist_ok=True)

    main_save_as = str(main_target_root / '{tag}' / '{frame}.png')
    main_include_layers = []
    main_ignore_layers = active_shadow_layers if split_shadow and active_shadow_layers else []
    main_cmd = build_export_cmd(
        aseprite=aseprite,
        src=src,
        save_as=main_save_as,
        include_layers=main_include_layers,
        ignore_layers=main_ignore_layers,
        preview=preview,
    )
    print(f'[INFO] Export main sprite -> {main_save_as}')
    run_export_command(main_cmd)

    if split_shadow and active_shadow_layers:
        shadow_save_as = str(shadow_target_root / '{tag}' / '{frame}.png')
        shadow_cmd = build_export_cmd(
            aseprite=aseprite,
            src=src,
            save_as=shadow_save_as,
            include_layers=active_shadow_layers,
            ignore_layers=[],
            preview=preview,
        )
        print(f'[INFO] Export shadow sprite -> {shadow_save_as}')
        run_export_command(shadow_cmd)


def main():
    parser = argparse.ArgumentParser(description='Extract per-tag frames from .aseprite files.')
    parser.add_argument('paths', nargs='+', help='Files, folders, or globs to scan')
    parser.add_argument('--aseprite', help='Path to aseprite.exe (or set ASEPRITE_EXE env var)')
    parser.add_argument('--output', default='assets', help='Output directory (default: assets)')
    parser.add_argument('--preview', action='store_true', help='Use Aseprite preview mode (no files written)')
    parser.add_argument(
        '--split-shadow',
        action='store_true',
        help='Split exports into main sprite (without shadow) and shadow-only output.',
    )
    parser.add_argument(
        '--shadow-layer',
        action='append',
        dest='shadow_layers',
        help='Shadow layer name (repeatable). Default: shadow.',
    )
    parser.add_argument(
        '--shadow-output',
        default='assets_shadow',
        help='Shadow output directory (default: assets_shadow).',
    )
    parser.add_argument(
        '--clean-target',
        action='store_true',
        help='Delete target sprite directory before exporting.',
    )
    parser.add_argument(
        '--clean-shadow-target',
        action='store_true',
        help='Delete shadow target sprite directory before exporting (requires --split-shadow).',
    )
    parser.add_argument(
        '--strict-shadow-layer',
        dest='strict_shadow_layer',
        action='store_true',
        help='Fail immediately when requested shadow layer is missing (default behavior).',
    )
    parser.add_argument(
        '--no-strict-shadow-layer',
        dest='strict_shadow_layer',
        action='store_false',
        help='Do not fail when requested shadow layer is missing.',
    )
    parser.set_defaults(strict_shadow_layer=True)
    args = parser.parse_args()

    aseprite = find_aseprite(args.aseprite)
    files = expand_inputs(args.paths)
    if not files:
        raise SystemExit('No .aseprite files found for given inputs.')
    if args.clean_shadow_target and not args.split_shadow:
        raise SystemExit('--clean-shadow-target requires --split-shadow.')

    shadow_layers = args.shadow_layers if args.shadow_layers else list(DEFAULT_SHADOW_LAYERS)
    if args.preview and args.clean_target:
        print('[PREVIEW] --clean-target requested; no directories will be deleted.')
    if args.preview and args.clean_shadow_target:
        print('[PREVIEW] --clean-shadow-target requested; no directories will be deleted.')

    for f in files:
        export_file(
            aseprite=aseprite,
            src=f,
            out_root=args.output,
            preview=args.preview,
            split_shadow=args.split_shadow,
            shadow_layers=shadow_layers,
            shadow_out_root=args.shadow_output,
            clean_target=args.clean_target,
            clean_shadow_target=args.clean_shadow_target,
            strict_shadow_layer=args.strict_shadow_layer,
        )


if __name__ == '__main__':
    main()
