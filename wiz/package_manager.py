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

            archive.extractall(dest)
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
                return str(data["name"]).replace("/", "_")
        except (OSError, ValueError):
            pass

    return fallback.replace("/", "_")


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

        name = _package_name_from_dir(extracted, repo)

        target = os.path.join(modules_dir, name)

        if os.path.exists(target):
            shutil.rmtree(target)

        os.makedirs(target, exist_ok=True)

        with Spinner("Installing"):
            for item in os.listdir(extracted):
                shutil.move(os.path.join(extracted, item), target)

        print(paint(
            f"  Installed '{name}' -> {target}",
            Color.GREEN
        ))

        installed[name] = spec

        dependencies = {}

        sub_manifest = os.path.join(target, MANIFEST_FILE)

        if os.path.exists(sub_manifest):
            try:
                with open(sub_manifest, encoding="utf-8") as file:
                    data = json.load(file)

                dependencies = (data.get("dependencies") or {})
            except (OSError, ValueError):
                dependencies = {}

        for dependency in dependencies.values():

            if dependency in visited:
                continue

            try:
                parse_spec(dependency)
            except WizError:
                continue

            visited.add(dependency)

            _install(dependency, base_path, visited, installed)

    except WizError:
        raise

    except urllib.error.URLError as error:
        raise WizError(
            f"Network error while fetching '{label}': {error.reason}"
        )

    finally:
        shutil.rmtree(staging, ignore_errors=True)


def install_package(spec, base_path="."):
    visited = {spec}
    installed = {}

    _install(spec, base_path, visited, installed)

    manifest = load_manifest(base_path)

    manifest["dependencies"].update(installed)

    save_manifest(manifest, base_path)

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

        if spec in visited:
            continue

        visited.add(spec)

        _install(spec, base_path, visited, installed)

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

    visited = {spec}
    installed = {}

    _install(spec, base_path, visited, installed)

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

        if spec in visited:
            continue

        visited.add(spec)

        _install(spec, base_path, visited, installed)

    manifest["dependencies"].update(installed)

    save_manifest(manifest, base_path)

    print(paint(f"  Updated {manifest_path(base_path)}", Color.CYAN))


def uninstall_package(name, base_path="."):
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


def list_packages(base_path="."):
    manifest = load_manifest(base_path)

    dependencies = manifest.get("dependencies", {})

    modules_dir = modules_path(base_path)

    if not dependencies:
        print("No packages installed")
        return

    for name, spec in dependencies.items():

        installed = os.path.isdir(
            os.path.join(modules_dir, name)
        )

        marker = "[installed]" if installed else "[missing]  "

        print(f"  {name:<24} {spec:<32} {marker}")
