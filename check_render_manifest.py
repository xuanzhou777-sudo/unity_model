"""Read-only PNG render provenance checks; no visual or historical acceptance."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def validate(data):
    errors = []
    try:
        if data.get("schema_version") != 1:
            raise ValueError("schema_version must be 1")
        root = Path(data["project_root"])
        if not root.is_absolute() or not root.is_dir():
            raise ValueError("project_root must be an existing absolute directory")
        root = root.resolve()
        asset_id = data["asset_id"]
        if not isinstance(asset_id, str) or not asset_id.strip():
            raise ValueError("asset_id must be a nonempty string")

        def resolve(value):
            path = Path(value)
            path = (path if path.is_absolute() else root / path).resolve()
            if not path.is_relative_to(root):
                raise ValueError("path escapes project_root: " + str(path))
            if not path.is_file():
                raise ValueError("missing file: " + str(path))
            return path

        model = data["model"]
        model_sha = model["sha256"]
        if not isinstance(model_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", model_sha):
            raise ValueError("model.sha256 must be lowercase SHA256")
        if digest(resolve(model["path"])) != model_sha:
            errors.append("model SHA256 changed")
        required = data["required_views"]
        if (not isinstance(required, list) or not required
                or any(not isinstance(view, str) or not view.strip() for view in required)
                or len(required) != len(set(required))):
            raise ValueError("required_views must contain unique nonempty view names")
        renders = data["renders"]
        if not isinstance(renders, list) or not renders:
            raise ValueError("renders must be a nonempty array")
        seen_views, seen_paths = set(), set()
        for index, render in enumerate(renders):
            prefix = "render[" + str(index) + "]: "
            try:
                view = render["view"]
                if not isinstance(view, str) or not view.strip():
                    raise ValueError("view must be a nonempty string")
                if view in seen_views:
                    errors.append(prefix + "duplicate view: " + view)
                seen_views.add(view)
                if render["asset_id"] != asset_id:
                    errors.append(prefix + "asset_id mismatch")
                if render["model_sha256"] != model_sha:
                    errors.append(prefix + "model_sha256 mismatch")
                path = resolve(render["path"])
                if path in seen_paths:
                    errors.append(prefix + "one file reused for multiple views")
                seen_paths.add(path)
                if digest(path) != render["sha256"]:
                    errors.append(prefix + "image SHA256 mismatch")
                with path.open("rb") as stream:
                    header = stream.read(24)
                if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n"
                        or header[8:16] != b"\x00\x00\x00\rIHDR"):
                    raise ValueError("expected PNG with IHDR header")
                actual = struct.unpack(">II", header[16:24])
                expected = (render["width"], render["height"])
                if (any(type(n) is not int or n <= 0 for n in expected)
                        or actual != expected):
                    errors.append(prefix + "PNG header dimensions mismatch")
            except (KeyError, TypeError, ValueError, OSError) as exc:
                errors.append(prefix + str(exc))
        missing = set(required) - seen_views
        if missing:
            errors.append("missing views: " + ", ".join(sorted(missing)))
    except (KeyError, TypeError, ValueError, OSError, AttributeError) as exc:
        errors.append(str(exc))
    return {"passed": not errors, "errors": errors,
            "scope": "provenance consistency and PNG header dimensions only"}


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError("usage: check_render_manifest.py <manifest.json>")
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
        result = validate(data)
    except (OSError, ValueError) as exc:
        result = {"passed": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
