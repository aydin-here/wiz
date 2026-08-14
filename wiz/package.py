import json
import os

from errors import (
    InvalidPackageManifestError,
    UnsupportedPackageTypeError,
    PackageError,
)

MANIFEST_FILE = "wiz.pkg"

WIZ_ENTRY_FILE = "main.wiz"
PYTHON_ENTRY_FILE = "main.py"

# A Wiz package is implemented in Wiz and its entry file is main.wiz.
PACKAGE_TYPE_WIZ = "wiz"

# A native package is implemented in Python and its entry file is main.py.
# "native" is the canonical value; "python" is accepted as a legacy alias
# and is normalized to "native" when a manifest is validated.
PACKAGE_TYPE_NATIVE = "native"
PACKAGE_TYPE_PYTHON = "python"

# When "type" is omitted from wiz.pkg it MUST default to "wiz".
DEFAULT_PACKAGE_TYPE = PACKAGE_TYPE_WIZ

SUPPORTED_PACKAGE_TYPES = (
    PACKAGE_TYPE_WIZ,
    PACKAGE_TYPE_NATIVE,
    PACKAGE_TYPE_PYTHON,
)


def is_python_package(pkg_type):
    """True for any type backed by a Python entry file (native or legacy)."""
    return pkg_type in (PACKAGE_TYPE_NATIVE, PACKAGE_TYPE_PYTHON)

# Interpreter version used to evaluate the optional "wiz_version"
# compatibility constraint in a package manifest.
WIZ_VERSION = "0.22.2"

#: Manifest schema (all fields optional unless marked required).
#:
#:   name         (str, required)  package name
#:   version      (str, required)  semantic version, e.g. "1.0.0"
#:   type         (str, optional)  "wiz" (default) or "native"
#:       ("python" is also accepted and treated as "native")
#:   description  (str, optional)  short human description
#:   author       (str, optional)  package author
#:   license      (str, optional)  license identifier, e.g. "MIT"
#:   repository   (str, optional)  source URL
#:   dependencies (dict, optional)  Wiz package dependencies (specs)
#:   python_dependencies (dict, optional)  Python modules required by a
#:       native package, mapped to optional version constraints.
#:   wiz_version  (str, optional)  minimum compatible interpreter version,
#:       e.g. ">=0.22.0"
MANIFEST_SCHEMA = {
    "name": "(str, required) package name",
    "version": "(str, required) semantic version, e.g. '1.0.0'",
    "type": "'wiz' (default when omitted) or 'native' (alias: 'python')",
    "description": "(str, optional) short human description",
    "author": "(str, optional) package author",
    "license": "(str, optional) license identifier, e.g. 'MIT'",
    "repository": "(str, optional) source URL",
    "dependencies": "(dict, optional) Wiz package dependencies (owner/repo specs)",
    "python_dependencies": "(dict, optional) Python modules required by a 'native' package",
    "wiz_version": "(str, optional) minimum compatible interpreter version, e.g. '>=0.22.0'",
}


def manifest_path(base_path):
    return os.path.join(base_path, MANIFEST_FILE)


def package_type(manifest):
    """Return the effective package type, defaulting to 'wiz'."""
    return manifest.get("type", DEFAULT_PACKAGE_TYPE)


def load_manifest(base_path):
    """Load and validate a package manifest from a package directory.

    Raises InvalidPackageManifestError when wiz.pkg is missing or invalid,
    and UnsupportedPackageTypeError when the declared type is not supported.
    """
    path = manifest_path(base_path)

    if not os.path.exists(path):
        raise InvalidPackageManifestError(
            f"Missing package manifest '{path}'",
            path=path
        )

    try:
        with open(path, encoding="utf-8") as file:
            manifest = json.load(file)
    except (OSError, ValueError) as error:
        raise InvalidPackageManifestError(
            f"Cannot read package manifest '{path}': {error}",
            path=path
        )

    return validate_manifest(manifest, path)


def validate_manifest(manifest, path=None):
    """Validate a parsed manifest dict, applying defaults in place."""

    if not isinstance(manifest, dict):
        raise InvalidPackageManifestError(
            f"Invalid package manifest '{path}': expected an object",
            path=path
        )

    name = manifest.get("name")

    if not name or not isinstance(name, str):
        raise InvalidPackageManifestError(
            f"Invalid package manifest '{path}': missing string field 'name'",
            path=path
        )

    version = manifest.get("version")

    if not version or not isinstance(version, str):
        raise InvalidPackageManifestError(
            f"Invalid package manifest '{path}': missing string field 'version'",
            path=path
        )

    dependencies = manifest.get("dependencies", {})

    if not isinstance(dependencies, dict):
        raise InvalidPackageManifestError(
            f"Invalid package manifest '{path}': "
            "'dependencies' must be an object",
            path=path
        )

    python_dependencies = manifest.get("python_dependencies", {})

    if not isinstance(python_dependencies, dict):
        raise InvalidPackageManifestError(
            f"Invalid package manifest '{path}': "
            "'python_dependencies' must be an object",
            path=path
        )

    # A missing "type" always defaults to "wiz".
    manifest.setdefault("type", DEFAULT_PACKAGE_TYPE)

    # "python" is a legacy alias for "native".
    if manifest["type"] == PACKAGE_TYPE_PYTHON:
        manifest["type"] = PACKAGE_TYPE_NATIVE

    pkg_type = package_type(manifest)

    if pkg_type not in SUPPORTED_PACKAGE_TYPES:
        raise UnsupportedPackageTypeError(
            f"Unsupported package type '{pkg_type}' for package '{name}'",
            path=path
        )

    return manifest


def check_wiz_version(manifest, path=None):
    """Verify the optional 'wiz_version' constraint against the interpreter.

    Raises PackageError when the running interpreter is incompatible so
    the package fails before any of its code is executed.
    """

    constraint = manifest.get("wiz_version")

    if not constraint:
        return

    if not version_satisfies(WIZ_VERSION, constraint):
        name = manifest.get("name", "?")
        raise PackageError(
            f"Package '{name}' requires wiz {constraint}, "
            f"but the running interpreter is wiz {WIZ_VERSION}",
            path=path
        )


def _parse_version(text):
    parts = []

    for part in str(text).lstrip("v").split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        parts.append(int(digits) if digits else 0)

    while len(parts) < 3:
        parts.append(0)

    return tuple(parts[:3])


def version_satisfies(version, constraint):
    version = str(version).strip()
    constraint = str(constraint).strip()

    if not constraint:
        return True

    for operator in (">=", "<=", "!=", "==", ">", "<"):
        if constraint.startswith(operator):
            target = constraint[len(operator):].strip()

            current = _parse_version(version)
            required = _parse_version(target)

            if operator == ">=":
                return current >= required
            if operator == "<=":
                return current <= required
            if operator == "!=":
                return current != required
            if operator == ">":
                return current > required
            if operator == "<":
                return current < required

            return current == required

    # A bare version number means "exactly this version".
    return _parse_version(version) == _parse_version(constraint)
