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
LAYER_EXPORT_FIELDS = {'name', 'output', 'layers', 'strict', 'clean'}
BOOL_VALUES = {
    '1': True,
    'true': True,
    'yes': True,
    'on': True,
    '0': False,
    'false': False,
    'no': False,
    'off': False,
}


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


def resolve_requested_layers(requested_layers, available_layers):
    available_lookup = {name.lower(): name for name in available_layers}
    resolved = []
    for layer_name in requested_layers:
        key = layer_name.lower()
        if key in available_lookup and available_lookup[key] not in resolved:
            resolved.append(available_lookup[key])
    return resolved


def parse_bool(value, field_name):
    normalized = value.strip().lower()
    if normalized not in BOOL_VALUES:
        raise SystemExit(
            f'Invalid boolean for {field_name}: {value}. '
            'Use one of: true, false, yes, no, on, off, 1, 0.'
        )
    return BOOL_VALUES[normalized]


def parse_layer_export_arg(raw):
    data = {}
    for segment in raw.split(';'):
        item = segment.strip()
        if not item:
            continue
        if '=' not in item:
            raise SystemExit(
                'Invalid --layer-export segment '
                f'"{item}". Expected key=value pairs separated by semicolons.'
            )
        key, value = item.split('=', 1)
        key = key.strip().lower()
        value = value.strip()
        if not key or not value:
            raise SystemExit(
                f'Invalid --layer-export segment "{item}". Empty key or value is not allowed.'
            )
        data[key] = value

    unknown_fields = sorted(set(data) - LAYER_EXPORT_FIELDS)
    if unknown_fields:
        raise SystemExit(
            'Unknown --layer-export fields: '
            f'{", ".join(unknown_fields)}. '
            'Supported fields: name, output, layers, strict, clean.'
        )

    missing_fields = [field for field in ('name', 'output', 'layers') if field not in data]
    if missing_fields:
        raise SystemExit(
            'Missing required --layer-export fields: '
            f'{", ".join(missing_fields)}.'
        )

    layers = [part.strip() for part in data['layers'].split(',') if part.strip()]
    if not layers:
        raise SystemExit('Invalid --layer-export layers list. Provide at least one layer name.')

    return {
        'name': data['name'],
        'output': data['output'],
        'layers': layers,
        'strict': parse_bool(data.get('strict', 'true'), 'strict'),
        'clean': parse_bool(data.get('clean', 'false'), 'clean'),
    }


def validate_layer_export_names(layer_exports):
    seen = {}
    for export_spec in layer_exports:
        key = export_spec['name'].lower()
        if key in seen:
            raise SystemExit(
                'Duplicate layer export name '
                f'"{export_spec["name"]}". '
                f'Already used by "{seen[key]}".'
            )
        seen[key] = export_spec['name']


def collect_layer_exports(args):
    layer_exports = []
    for raw in args.layer_export or []:
        layer_exports.append(parse_layer_export_arg(raw))

    if args.split_shadow:
        shadow_layers = args.shadow_layers if args.shadow_layers else list(DEFAULT_SHADOW_LAYERS)
        layer_exports.append(
            {
                'name': 'shadow',
                'output': args.shadow_output,
                'layers': shadow_layers,
                'strict': args.strict_shadow_layer,
                'clean': args.clean_shadow_target,
            }
        )

    validate_layer_export_names(layer_exports)
    return layer_exports


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


def build_export_cmd(
    aseprite,
    src,
    save_as,
    include_layers,
    ignore_layers,
    preview,
    tag_filters=None,
):
    cmd = [aseprite, '-b', '--split-tags']
    for tag_name in tag_filters or []:
        cmd.extend(['--tag', tag_name])
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


def prepare_layer_exports(aseprite, src, layer_exports, requested_main_ignore_layers=None):
    requested_main_ignore_layers = requested_main_ignore_layers or []
    if not layer_exports and not requested_main_ignore_layers:
        return [], []

    available_layers = list_layers(aseprite, src)
    print(f'[INFO] Sprite: {src}')
    print(f'[INFO] Available layers: {", ".join(available_layers) if available_layers else "<none>"}')

    active_exports = []
    main_ignore_layers = []
    for export_spec in layer_exports:
        matched_layers = resolve_requested_layers(export_spec['layers'], available_layers)
        print(f'[INFO] Layer export: {export_spec["name"]}')
        print(f'[INFO] Requested layers: {", ".join(export_spec["layers"])}')
        print(f'[INFO] Matched layers: {", ".join(matched_layers) if matched_layers else "<none>"}')
        if not matched_layers:
            error_message = (
                f'No layer matched for export "{export_spec["name"]}" in {src}. '
                f'Requested={export_spec["layers"]}, Available={available_layers}'
            )
            if export_spec['strict']:
                raise SystemExit(error_message)
            print(f'[WARN] {error_message}')
            continue

        normalized_export = dict(export_spec)
        normalized_export['matched_layers'] = matched_layers
        active_exports.append(normalized_export)
        for layer_name in matched_layers:
            if layer_name not in main_ignore_layers:
                main_ignore_layers.append(layer_name)

    for requested_layer in requested_main_ignore_layers:
        matched_layers = resolve_requested_layers([requested_layer], available_layers)
        if not matched_layers:
            print(
                f'[WARN] Main ignore layer not found in {src}: "{requested_layer}". '
                f'Available={available_layers}'
            )
            continue
        for layer_name in matched_layers:
            if layer_name not in main_ignore_layers:
                main_ignore_layers.append(layer_name)

    return active_exports, main_ignore_layers


def export_file(
    aseprite,
    src,
    out_root,
    preview=False,
    clean_target=False,
    layer_exports=None,
    main_ignore_layers=None,
    tag_filters=None,
):
    base = src.stem
    main_target_root = Path(out_root) / base

    if clean_target:
        clean_target_directory(main_target_root, preview)

    active_layer_exports, main_ignore_layers = prepare_layer_exports(
        aseprite=aseprite,
        src=src,
        layer_exports=layer_exports or [],
        requested_main_ignore_layers=main_ignore_layers or [],
    )

    for export_spec in active_layer_exports:
        export_target_root = Path(export_spec['output']) / base
        if export_spec['clean']:
            clean_target_directory(export_target_root, preview)

    if not preview:
        main_target_root.mkdir(parents=True, exist_ok=True)
        for export_spec in active_layer_exports:
            export_target_root = Path(export_spec['output']) / base
            export_target_root.mkdir(parents=True, exist_ok=True)

    main_save_as = str(main_target_root / '{tag}' / '{frame}.png')
    main_cmd = build_export_cmd(
        aseprite=aseprite,
        src=src,
        save_as=main_save_as,
        include_layers=[],
        ignore_layers=main_ignore_layers,
        preview=preview,
        tag_filters=tag_filters or [],
    )
    print(f'[INFO] Export main sprite -> {main_save_as}')
    run_export_command(main_cmd)

    for export_spec in active_layer_exports:
        export_target_root = Path(export_spec['output']) / base
        export_save_as = str(export_target_root / '{tag}' / '{frame}.png')
        export_cmd = build_export_cmd(
            aseprite=aseprite,
            src=src,
            save_as=export_save_as,
            include_layers=export_spec['matched_layers'],
            ignore_layers=[],
            preview=preview,
            tag_filters=tag_filters or [],
        )
        print(f'[INFO] Export {export_spec["name"]} sprite -> {export_save_as}')
        run_export_command(export_cmd)


def main():
    parser = argparse.ArgumentParser(description='Extract per-tag frames from .aseprite files.')
    parser.add_argument('paths', nargs='+', help='Files, folders, or globs to scan')
    parser.add_argument('--aseprite', help='Path to aseprite.exe (or set ASEPRITE_EXE env var)')
    parser.add_argument('--output', default='assets', help='Output directory (default: assets)')
    parser.add_argument('--preview', action='store_true', help='Use Aseprite preview mode (no files written)')
    parser.add_argument(
        '--layer-export',
        action='append',
        help=(
            'Repeatable layer export spec. Format: '
            '"name=<group>;output=<dir>;layers=<layer1,layer2>[;strict=true|false][;clean=true|false]"'
        ),
    )
    parser.add_argument(
        '--split-shadow',
        action='store_true',
        help='Legacy helper: split exports into main sprite (without shadow) and shadow-only output.',
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
        '--main-ignore-layer',
        action='append',
        dest='main_ignore_layers',
        help='Exclude layer from main sprite export (repeatable).',
    )
    parser.add_argument(
        '--tag',
        action='append',
        dest='tags',
        help='Export only selected tag(s), repeatable.',
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

    if args.clean_shadow_target and not args.split_shadow:
        raise SystemExit('--clean-shadow-target requires --split-shadow.')

    aseprite = find_aseprite(args.aseprite)
    files = expand_inputs(args.paths)
    if not files:
        raise SystemExit('No .aseprite files found for given inputs.')

    layer_exports = collect_layer_exports(args)

    if args.preview and args.clean_target:
        print('[PREVIEW] --clean-target requested; no directories will be deleted.')
    if args.preview and args.clean_shadow_target:
        print('[PREVIEW] --clean-shadow-target requested; no directories will be deleted.')

    for src in files:
        export_file(
            aseprite=aseprite,
            src=src,
            out_root=args.output,
            preview=args.preview,
            clean_target=args.clean_target,
            layer_exports=layer_exports,
            main_ignore_layers=args.main_ignore_layers or [],
            tag_filters=args.tags or [],
        )


if __name__ == '__main__':
    main()
