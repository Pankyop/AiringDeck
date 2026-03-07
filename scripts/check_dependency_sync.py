import argparse
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


ALLOWED_REQUIREMENTS_ONLY = {
    "pyinstaller",  # Build-time dependency, intentionally excluded from project runtime deps.
}


def _load_requirements(requirements_path: Path) -> dict[str, Requirement]:
    out: dict[str, Requirement] = {}
    for lineno, line in enumerate(requirements_path.read_text(encoding="utf-8").splitlines(), start=1):
        raw = line.split("#", 1)[0].strip()
        if not raw:
            continue
        if raw.startswith(("-r", "--")):
            continue
        try:
            req = Requirement(raw)
        except Exception as exc:
            raise ValueError(f"{requirements_path}:{lineno}: invalid requirement '{raw}': {exc}") from exc
        out[canonicalize_name(req.name)] = req
    return out


def _load_project_dependencies(pyproject_path: Path) -> dict[str, Requirement]:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    deps = (data.get("project") or {}).get("dependencies") or []
    out: dict[str, Requirement] = {}
    for idx, dep in enumerate(deps, start=1):
        try:
            req = Requirement(dep)
        except Exception as exc:
            raise ValueError(f"{pyproject_path}: project.dependencies[{idx}] invalid ('{dep}'): {exc}") from exc
        out[canonicalize_name(req.name)] = req
    return out


def _extract_exact_pin(req: Requirement) -> str | None:
    specs = list(req.specifier)
    if len(specs) != 1:
        return None
    spec = specs[0]
    if spec.operator == "==":
        return spec.version
    return None


def _validate_sync(
    requirements: dict[str, Requirement],
    project_dependencies: dict[str, Requirement],
) -> list[str]:
    errors: list[str] = []

    missing_in_requirements = sorted(set(project_dependencies) - set(requirements))
    if missing_in_requirements:
        errors.append(
            "Missing in requirements.txt: "
            + ", ".join(missing_in_requirements)
        )

    extras_in_requirements = sorted(
        set(requirements) - set(project_dependencies) - ALLOWED_REQUIREMENTS_ONLY
    )
    if extras_in_requirements:
        errors.append(
            "Present only in requirements.txt (not allowed extras): "
            + ", ".join(extras_in_requirements)
        )

    for name in sorted(set(requirements).intersection(project_dependencies)):
        req_pin = _extract_exact_pin(requirements[name])
        proj_spec = project_dependencies[name].specifier
        if req_pin is None or not proj_spec:
            continue
        if req_pin not in proj_spec:
            errors.append(
                f"Version mismatch for '{name}': requirements pins '{req_pin}' but pyproject expects '{proj_spec}'"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate dependency sync between requirements.txt and pyproject.toml."
    )
    parser.add_argument(
        "--requirements",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)",
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        help="Path to pyproject file (default: pyproject.toml)",
    )
    args = parser.parse_args()

    requirements_path = Path(args.requirements).resolve()
    pyproject_path = Path(args.pyproject).resolve()

    try:
        requirements = _load_requirements(requirements_path)
        project_dependencies = _load_project_dependencies(pyproject_path)
        errors = _validate_sync(requirements, project_dependencies)
    except Exception as exc:
        print(f"Dependency sync check failed to run: {exc}")
        return 1

    if errors:
        print("Dependency sync check: FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Dependency sync check: PASSED")
    print(
        f"Compared {len(project_dependencies)} project dependencies with "
        f"{len(requirements)} requirements entries."
    )
    if ALLOWED_REQUIREMENTS_ONLY:
        extras = ", ".join(sorted(ALLOWED_REQUIREMENTS_ONLY))
        print(f"Allowed requirements-only extras: {extras}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
