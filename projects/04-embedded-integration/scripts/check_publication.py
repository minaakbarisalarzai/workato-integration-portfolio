"""Conservative scan for common accidental secret patterns and risky file types.

Not a replacement for GitHub secret scanning or gitleaks.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', 'node_modules'}
BANNED = {'.pem', '.key', '.p12', '.pfx', '.zip'}
PATTERNS = {
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'Workato token': re.compile(r'wrkaus-[A-Za-z0-9_.-]{25,}'),
    'AWS access key': re.compile(r'AKIA[0-9A-Z]{16}'),
}


def main():
    warnings = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(p in SKIP for p in path.parts) or path.name == Path(__file__).name:
            continue
        if path.suffix in BANNED or path.name == '.env':
            warnings.append(f'blocked file type: {path.relative_to(ROOT)}')
            continue
        try:
            contents = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(contents):
                warnings.append(f'possible {label}: {path.relative_to(ROOT)}')
    if warnings:
        for warning in warnings:
            print(warning)
        return 1
    print('Publication precheck: no common risky patterns detected (not comprehensive).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
