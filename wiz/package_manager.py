import json
import os
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from errors import WizError
from ui import Color, Spinner, download, paint
from package import (
    load_manifest as load_package_manifest,
    package_type,
    validate_manifest,
    manifest_path as package_manifest_path,
    PYTHON_ENTRY_FILE,
)


MANIFEST_FILE = "wiz.pkg"
MODULES_DIR = "wiz_modules"

GITHUB = "https://github.com"
USER_AGENT = "wiz-package-manager"


def manifest_path(base_path="."):
    return os.path.join(base_path, MANIFEST_FILE)


def modules_path(base_path="."):
    return os.path.join(base_path, MODULES_DIR)


def load_manifest(base_path="."):
    path = manifest_path(base_path)

    default = {
        "name": os.path.basename(os.path.abspath(base_path)),
        "version": "0.0.0",
        "dependencies": {},
    }

    if not os.path.exists(path):
        return default

    try:
        with open(path, encoding="utf-8") as file:
            manifest = json.load(file)
    except (OSError, ValueError) as error:
        raise WizError(f"Cannot read '{path}': {error}")

    if not isinstance(manifest, dict):
        raise WizError(f"Invalid manifest '{path}'")

    manifest.setdefault("name", default["name"])
    manifest.setdefault("version", default["version"])
    manifest.setdefault("dependencies", {})

    return manifest


def save_manifest(manifest, base_path="."):
    with open(manifest_path(base_path), "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)
        file.write("\n")


def parse_spec(spec):
    spec = spec.strip()

    tag = None

    if "@" in spec:
        spec, tag = spec.rsplit("@", 1)

    if "/" not in spec:
        raise WizError(
            f"Invalid package '{spec}'. Expected 'owner/repo[@tag]'."
        )

    owner, repo = spec.split("/", 1)

    if not owner or not repo:
        raise WizError(f"Invalid package '{spec}'.")

    return owner, repo, tag


def sanitize_package_name(name, fallback):
    """Make a package name safe to use as a single install directory."""

    name = str(name or "").strip().replace("\\", "/")

    parts = name.split("/")

    if not name or not parts[0] or name.startswith("/") or ".." in parts:
        name = str(fallback).replace("/", "_")

    name = name.replace("/", "_").lstrip(".")

    if not name or name in (".", ".."):
        return "_package"

    return name


def _fetch_archive(owner, repo, tag, dest):
    repo_quoted = urllib.parse.quote(repo, safe="")
    temporary = dest + ".tmp"
    label = f"Downloading {owner}/{repo}"

    def try_url(url):
        download(url, temporary, label=label, user_agent=USER_AGENT)
        os.replace(temporary, dest)

    try:
        if tag:
            tag_quoted = urllib.parse.quote(tag, safe="")
            url = f"{GITHUB}/{owner}/{repo_quoted}/archive/refs/tags/{tag_quoted}.tar.gz"
            try_url(url)
            return
    except urllib.error.HTTPError as error:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise WizError(
            f"Package '{owner}/{repo}@{tag}' not found (HTTP {error.code})."
        )

    last_error = None

    for branch in ("main", "master"):
        url = f"{GITHUB}/{owner}/{repo_quoted}/archive/refs/heads/{branch}.tar.gz"
        try:
            try_url(url)
            return
        except urllib.error.HTTPError as error:
            last_error = error
            if os.path.exists(temporary):
                os.remove(temporary)

    raise WizError(
        f"Package '{owner}/{repo}' not found (HTTP {last_error.code})."
    )


def _extract(tarball_path, dest):
    os.makedirs(dest, exist_ok=True)

    try:
        with tarfile.open(tarball_path, "r:gz") as archive:
            members = archive.getmembers()

            if not members:
                raise WizError("Package archive is empty.")

            root = members[0].name.split("/", 1)[0]

            for member in members:

                # Reject path traversal and absolute paths so a package
                # archive can never write outside its install directory.
                if member.name.startswith("/") or ".." in member.name.split("/"):
                    raise WizError(
                        f"Package archive contains an invalid path "
                        f"'{member.name}'"
                    )

            archive.extractall(dest)
    except WizError:
        raise
    except (tarfile.TarError, OSError) as error:
        raise WizError(f"Could not extract package: {error}")

    source = os.path.join(dest, root)

    if os.path.isdir(source):
        for item in os.listdir(source):
            shutil.move(os.path.join(source, item), dest)
        os.rmdir(source)


def _package_name_from_dir(directory, fallback):
    manifest = os.path.join(directory, MANIFEST_FILE)

    if os.path.exists(manifest):
        try:
            with open(manifest, encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict) and data.get("name"):
                return sanitize_package_name(data["name"], fallback)
        except (OSError, ValueError):
            pass

    return sanitize_package_name(fallback, fallback)


def _is_local_spec(spec):
    return (
        isinstance(spec, str)
        and (spec.startswith(("./", "../", ".")) or os.sep in spec)
    )


def _copy_contents(source, target):
    for item in os.listdir(source):
        src = os.path.join(source, item)
        dest = os.path.join(target, item)

        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)


def _install_extracted(source, base_path, fallback, visited, installed, spec=None):
    """Install a package from an extracted or local directory.

    Reads and validates wiz.pkg, defaults a missing package type to "wiz",
    copies the package into wiz_modules/ and records it as installed.
    Reinstalling over an existing directory replaces it in place, which is
    the offline equivalent of 'wiz update'.
    """

    source_key = os.path.abspath(source)

    if source_key in visited:
        return

    visited.add(source_key)

    modules_dir = modules_path(base_path)

    os.makedirs(modules_dir, exist_ok=True)

    manifest_file = os.path.join(source, MANIFEST_FILE)

    if os.path.exists(manifest_file):

        manifest = load_package_manifest(source)

        name = sanitize_package_name(manifest["name"], fallback)
        dependencies = manifest.get("dependencies", {}) or {}
        pkg_type = package_type(manifest)

    else:

        manifest = None
        name = sanitize_package_name(fallback, fallback)
        dependencies = {}
        pkg_type = "unknown"

    target = os.path.join(modules_dir, name)

    if os.path.exists(target):
        shutil.rmtree(target)

    os.makedirs(target, exist_ok=True)

    with Spinner("Installing"):
        _copy_contents(source, target)

    print(paint(
        f"  Installed '{name}' -> {target}",
        Color.GREEN
    ))

    installed[name] = spec if spec else os.path.abspath(source)

    if manifest and manifest.get("python_dependencies"):
        print(paint(
            f"  '{name}' requires Python packages: "
            + ", ".join(manifest["python_dependencies"])
            + ". Install them with pip.",
            Color.YELLOW
        ))

    for dependency in dependencies.values():

        if dependency in visited:
            continue

        if _is_local_spec(dependency):

            local_path = dependency

            if not os.path.isabs(local_path):
                local_path = os.path.join(source, local_path)

            local_path = os.path.abspath(local_path)

            if os.path.isdir(local_path):
                visited.add(dependency)
                _install_extracted(
                    local_path,
                    base_path,
                    os.path.basename(local_path),
                    visited,
                    installed,
                    spec=dependency
                )

            continue

        try:
            parse_spec(dependency)
        except WizError:
            continue

        visited.add(dependency)

        _install(dependency, base_path, visited, installed)


def _install(spec, base_path, visited, installed):
    owner, repo, tag = parse_spec(spec)

    modules_dir = modules_path(base_path)

    os.makedirs(modules_dir, exist_ok=True)

    label = f"{owner}/{repo}" + (f"@{tag}" if tag else "")

    staging = tempfile.mkdtemp(prefix="wiz-pkg-")

    try:
        tarball = os.path.join(staging, "package.tar.gz")

        _fetch_archive(owner, repo, tag, tarball)

        extracted = os.path.join(staging, "src")

        with Spinner(f"Extracting {label}"):
            _extract(tarball, extracted)

        fallback = _package_name_from_dir(extracted, repo)

        _install_extracted(
            extracted,
            base_path,
            fallback,
            visited,
            installed,
            spec=spec
        )

    except WizError:
        raise

    except urllib.error.URLError as error:
        raise WizError(
            f"Network error while fetching '{label}': {error.reason}"
        )

    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _install_spec(spec, base_path, visited, installed):
    """Install a dependency spec, routing local paths to the offline path."""

    if _is_local_spec(spec):

        if not os.path.isdir(spec):
            raise WizError(f"Local package path '{spec}' does not exist")

        if spec in visited:
            return

        visited.add(spec)

        fallback = os.path.basename(os.path.abspath(spec))

        _install_extracted(
            spec,
            base_path,
            fallback,
            visited,
            installed,
            spec=spec
        )

        return

    if spec in visited:
        return

    visited.add(spec)

    _install(spec, base_path, visited, installed)


def install_package(spec, base_path="."):
    visited = set()
    installed = {}

    _install_spec(spec, base_path, visited, installed)

    manifest = load_manifest(base_path)

    manifest["dependencies"].update(installed)

    save_manifest(manifest, base_path)

    print(paint(f"  Updated {manifest_path(base_path)}", Color.CYAN))


def install_from_directory(source, base_path="."):
    """Install a package from a local directory without network access.

    The directory must contain a valid wiz.pkg manifest. Package files are
    copied into wiz_modules/ and the dependency is recorded in wiz.pkg.
    """

    source = os.path.abspath(source)

    manifest = load_package_manifest(source)

    visited = set()
    installed = {}

    _install_extracted(
        source,
        base_path,
        manifest["name"],
        visited,
        installed
    )

    project_manifest = load_manifest(base_path)

    project_manifest["dependencies"].update(installed)

    save_manifest(project_manifest, base_path)

    print(paint(f"  Updated {manifest_path(base_path)}", Color.CYAN))


def install_all(base_path="."):
    manifest = load_manifest(base_path)

    dependencies = manifest.get("dependencies", {})

    if not dependencies:
        print("No dependencies in wiz.pkg")
        return

    visited = set()
    installed = {}

    for spec in dependencies.values():
        _install_spec(spec, base_path, visited, installed)

    manifest["dependencies"].update(installed)

    save_manifest(manifest, base_path)

    print(paint(f"  Updated {manifest_path(base_path)}", Color.CYAN))


def _unpin_spec(spec):
    owner, repo, _ = parse_spec(spec)
    return f"{owner}/{repo}"


def update_package(name, base_path="."):
    manifest = load_manifest(base_path)

    dependencies = manifest.get("dependencies", {})

    if name not in dependencies:
        raise WizError(
            f"Package '{name}' is not installed. "
            "Run 'wiz install <owner/repo>' first."
        )

    spec = _unpin_spec(dependencies[name])

    visited = set()
    installed = {}

    _install_spec(spec, base_path, visited, installed)

    manifest["dependencies"].update(installed)

    save_manifest(manifest, base_path)

    print(paint(f"  Updated {manifest_path(base_path)}", Color.CYAN))


def update_all(base_path="."):
    manifest = load_manifest(base_path)

    dependencies = manifest.get("dependencies", {})

    if not dependencies:
        print("No dependencies in wiz.pkg")
        return

    visited = set()
    installed = {}

    for spec in dependencies.values():

        spec = _unpin_spec(spec)

        _install_spec(spec, base_path, visited, installed)

    manifest["dependencies"].update(installed)

    save_manifest(manifest, base_path)

    print(paint(f"  Updated {manifest_path(base_path)}", Color.CYAN))


def uninstall_package(name, base_path="."):
    name = sanitize_package_name(name, name)

    target = os.path.join(modules_path(base_path), name)

    manifest = load_manifest(base_path)

    removed = False

    if os.path.exists(target):
        shutil.rmtree(target)
        removed = True

    if name in manifest["dependencies"]:
        del manifest["dependencies"][name]
        save_manifest(manifest, base_path)
        removed = True

    if removed:
        print(paint(f"Uninstalled '{name}'", Color.GREEN))
    else:
        print(f"Package '{name}' is not installed")


def _package_manifest_info(directory):
    """Return (type, version) for an installed package directory."""

    manifest_file = os.path.join(directory, MANIFEST_FILE)

    if not os.path.isfile(manifest_file):
        return "unknown", "?"

    try:
        with open(manifest_file, encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return "unknown", "?"

    if not isinstance(data, dict):
        return "unknown", "?"

    try:
        validate_manifest(data)
    except Exception:
        return "unknown", str(data.get("version") or "?")

    return package_type(data), str(data.get("version") or "?")


def list_packages(base_path="."):
    manifest = load_manifest(base_path)

    dependencies = manifest.get("dependencies", {})

    modules_dir = modules_path(base_path)

    if not dependencies:
        print("No packages installed")
        return

    print("  Installed packages:")
    print()

    for name, spec in dependencies.items():

        directory = os.path.join(modules_dir, name)

        installed = os.path.isdir(directory)

        pkg_type, version = _package_manifest_info(directory)

        suffix = "" if installed else "  [missing]"

        print(f"  {name:<24} {version:<12} [{pkg_type}]{suffix}")


def info_package(name, base_path="."):
    directory = os.path.join(
        modules_path(base_path),
        sanitize_package_name(name, name)
    )

    if not os.path.isdir(directory):
        raise WizError(f"Package '{name}' is not installed")

    manifest_file = os.path.join(directory, MANIFEST_FILE)

    if not os.path.isfile(manifest_file):
        raise WizError(f"Package '{name}' has no '{MANIFEST_FILE}' manifest")

    manifest = load_package_manifest(directory)

    print(f"  name         : {manifest.get('name', name)}")
    print(f"  version      : {manifest.get('version', '?')}")
    print(f"  type         : {package_type(manifest)}")
    print(f"  description  : {manifest.get('description', '-')}")
    print(f"  author       : {manifest.get('author', '-')}")
    print(f"  license      : {manifest.get('license', '-')}")
    print(f"  repository   : {manifest.get('repository', '-')}")

    dependencies = manifest.get("dependencies", {})
    print(f"  dependencies : {', '.join(dependencies) or '-'}")

    python_dependencies = manifest.get("python_dependencies", {})
    print(f"  python deps  : {', '.join(python_dependencies) or '-'}")

    print(f"  path         : {directory}")
