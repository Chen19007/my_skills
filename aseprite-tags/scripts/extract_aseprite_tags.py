import argparse
import glob
import json
import struct
from pathlib import Path

DIRECTION = {0: 'forward', 1: 'reverse', 2: 'pingpong'}


def read_u16(data, off):
    return struct.unpack_from('<H', data, off)[0]


def read_u32(data, off):
    return struct.unpack_from('<I', data, off)[0]


def parse_tags_from_chunk(chunk):
    tags = []
    p = 0
    if len(chunk) < 10:
        return tags
    num = read_u16(chunk, p)
    p += 2
    p += 8  # reserved
    for _ in range(num):
        if p + 2 > len(chunk):
            break
        frm = read_u16(chunk, p)
        p += 2
        to = read_u16(chunk, p)
        p += 2
        if p + 1 > len(chunk):
            break
        direction = chunk[p]
        p += 1
        if p + 8 > len(chunk):
            break
        p += 8  # reserved
        if p + 4 > len(chunk):
            break
        r, g, b = chunk[p], chunk[p + 1], chunk[p + 2]
        p += 4  # includes reserved byte
        if p + 2 > len(chunk):
            break
        name_len = read_u16(chunk, p)
        p += 2
        if p + name_len > len(chunk):
            break
        name = chunk[p:p + name_len].decode('utf-8', 'replace')
        p += name_len
        tags.append({
            'from': frm,
            'to': to,
            'direction': DIRECTION.get(direction, str(direction)),
            'color': [r, g, b],
            'name': name,
        })
    return tags


def parse_aseprite_tags(path):
    data = path.read_bytes()
    if len(data) < 128:
        return []
    magic = read_u16(data, 4)
    if magic != 0xA5E0:
        return []
    frames = read_u16(data, 6)
    offset = 128
    tags = []
    for _ in range(frames):
        if offset + 16 > len(data):
            break
        frame_bytes = read_u32(data, offset)
        frame_magic = read_u16(data, offset + 4)
        if frame_magic != 0xF1FA:
            break
        old_chunks = read_u16(data, offset + 6)
        new_chunks = read_u32(data, offset + 12)
        chunks = new_chunks if new_chunks != 0 else old_chunks
        pos = offset + 16
        for _c in range(chunks):
            if pos + 6 > len(data):
                break
            chunk_size = read_u32(data, pos)
            chunk_type = read_u16(data, pos + 4)
            chunk_start = pos + 6
            chunk_end = pos + chunk_size
            if chunk_end > len(data):
                break
            if chunk_type == 0x2018:
                chunk = data[chunk_start:chunk_end]
                tags.extend(parse_tags_from_chunk(chunk))
            pos += chunk_size
        offset += frame_bytes
    return tags


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


def main():
    parser = argparse.ArgumentParser(description='Extract Aseprite tag metadata.')
    parser.add_argument('paths', nargs='+', help='Files, folders, or globs to scan')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()

    files = expand_inputs(args.paths)
    if not files:
        raise SystemExit('No .aseprite files found for given inputs.')

    if args.json:
        payload = []
        for f in files:
            tags = parse_aseprite_tags(f)
            dedup = []
            seen = set()
            for t in tags:
                key = (t['name'], t['from'], t['to'], t['direction'], tuple(t['color']))
                if key in seen:
                    continue
                seen.add(key)
                dedup.append(t)
            payload.append({'file': str(f), 'tags': dedup})
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return

    for f in files:
        tags = parse_aseprite_tags(f)
        print(f'## {f.name}')
        if not tags:
            print('- (no tags found)')
            print()
            continue
        seen = set()
        for t in tags:
            key = (t['name'], t['from'], t['to'], t['direction'])
            if key in seen:
                continue
            seen.add(key)
            name = t['name'] if t['name'] else '(unnamed)'
            print(f"- {name}: {t['from']}-{t['to']} ({t['direction']})")
        print()


if __name__ == '__main__':
    main()
