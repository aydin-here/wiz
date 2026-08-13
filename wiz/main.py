import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import WizError
from package_manager import (
    install_package,
    install_all,
    update_package,
    update_all,
    uninstall_package,
    list_packages
)
from linter import Linter
from ui import Color, Spinner, download, paint, ssl_context, success

VERSION = "0.21.9"
BANNER = """__        ___     
\ \      / (_)____
 \ \ /\ / /| |_  /
  \ V  V / | |/ / 
   \_/\_/  |_/___|
"""

REPO_OWNER = "aydin-here"
REPO_NAME = "wiz"
RELEASE_API = (
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
)
DOWNLOAD_BASE = (
    f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download"
)
SOURCE_TARBALL = (
    f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/tags"
)
USER_AGENT = "wiz-self-updater"


def load_file(filename):
    if not filename.endswith(".wiz"):
        print("Error: expected a .wiz file")
        sys.exit(1)

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: '{filename}' not found")
        sys.exit(1)


def print_help():
    print(f"""
Wiz Programming Language v{VERSION}

Usage:
    wiz <command> [args...]

Commands:
    run <file.wiz>                Execute a Wiz program
    tokens <file.wiz>             Print lexer tokens
    ast <file.wiz>                Print parsed AST
    lint <file.wiz>               Statically analyze a Wiz file
    install [owner/repo[@tag]]    Install all dependencies or a package
    update [package]              Update all packages or a specific one
    -U, upgrade                   Update Wiz itself from GitHub
    uninstall <package>           Remove an installed package
    list                          List installed packages
    version                       Show language version
    help                          Show this help
""")


def print_version():
    print(BANNER)
    print(f"Wiz Programming Language v{VERSION}")


def parse_version(text):
    version = str(text).lstrip("v")

    parts = []

    for part in version.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        parts.append(int(digits) if digits else 0)

    while len(parts) < 3:
        parts.append(0)

    return tuple(parts[:3])


def _request(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )
    context = ssl_context()

    return urllib.request.urlopen(request, timeout=20, context=context)


def latest_release():
    try:
        with _request(RELEASE_API) as response:
            data = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as error:
        raise WizError(f"Cannot reach GitHub releases: {error}")

    tag = data.get("tag_name", "")

    if not tag:
        raise WizError("GitHub returned no release information.")

    assets = {
        asset["name"]: asset["browser_download_url"]
        for asset in data.get("assets", [])
    }

    return tag, assets


def _platform_asset():
    if sys.platform.startswith("win"):
        return "wiz-windows.exe"
    if sys.platform == "darwin":
        return "wiz-macos"
    return "wiz-linux"


def _package_root():
    return os.path.dirname(os.path.abspath(__file__))


def _update_source(tag):
    root = _package_root()

    staging = tempfile.mkdtemp(prefix="wiz-update-")

    try:
        tarball = os.path.join(staging, "source.tar.gz")

        download(
            f"{SOURCE_TARBALL}/{tag}.tar.gz",
            tarball,
            label=f"Downloading source {tag}"
        )

        extracted = os.path.join(staging, "src")
        os.makedirs(extracted)

        with Spinner("Extracting source"):
            with tarfile.open(tarball, "r:gz") as archive:
                archive.extractall(extracted)

        entries = os.listdir(extracted)

        if not entries:
            raise WizError("Downloaded source is empty.")

        source = os.path.join(extracted, entries[0], "wiz")

        if not os.path.isdir(source):
            raise WizError("Downloaded source has no 'wiz' package.")

        for item in os.listdir(source):

            src = os.path.join(source, item)
            dest = os.path.join(root, item)

            if os.path.isdir(src):
                shutil.rmtree(dest, ignore_errors=True)
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)

        success(f"  Updated source to {tag}.")
        return True

    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _replace_executable(exe, new_path):
    try:
        os.replace(new_path, exe)
        return True
    except OSError:
        return False


def update_self(check_only=False):
    print(f"  Current version : v{VERSION}")

    with Spinner("Checking latest release"):
        tag, assets = latest_release()

    latest = parse_version(tag)

    print(f"  Latest release  : {tag}")

    if latest <= parse_version(VERSION):
        success("  Already up to date.")
        return False

    print(paint(f"  Update available: v{VERSION} -> {tag}", Color.BOLD))

    if check_only:
        return True

    if getattr(sys, "frozen", False):
        asset = _platform_asset()

        if asset not in assets:
            raise WizError(
                f"No '{asset}' binary in release {tag}."
            )

        exe = os.path.abspath(sys.executable)

        new_path = exe + ".new"

        try:
            download(assets[asset], new_path, label=f"Downloading {asset}")
        except (urllib.error.URLError, OSError) as error:
            if os.path.exists(new_path):
                os.remove(new_path)
            raise WizError(f"Download failed: {error}")

        os.chmod(new_path, 0o755)

        if _replace_executable(exe, new_path):
            success(f"  Updated to {tag}. Restart wiz to use it.")
        else:
            print(
                f"  New binary saved to '{new_path}'.\n"
                "  The running executable could not be replaced.\n"
                "  Move it over the current wiz executable to finish."
            )

        return True

    return _update_source(tag)


def run(filename):
    source = load_file(filename)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        tree = parser.parse()

        interpreter = Interpreter(os.path.dirname(filename))
        interpreter.visit(tree)

    except WizError as e:
        e.attach_source(source)
        e.filename = filename
        print(e)
        sys.exit(1)
    except Exception as e:
        print("┌──────────────────────────────┐")
        print("│        INTERNAL WIZ ERROR    │")
        print("└──────────────────────────────┘")
        print()
        print(f"An unexpected error occurred in {filename}:")
        print()
        print(f"  {type(e).__name__}: {e}")
        sys.exit(1)


def print_tokens(filename):
    source = load_file(filename)

    try:
        lexer = Lexer(source)

        for token in lexer.tokenize():
            print(token)
    except WizError as e:
        e.attach_source(source)
        e.filename = filename
        print(e)
        sys.exit(1)


def print_ast(filename):
    source = load_file(filename)

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)

        tree = parser.parse()

        print(tree)
    except WizError as e:
        e.attach_source(source)
        e.filename = filename
        print(e)
        sys.exit(1)


def lint(filename):
    source = load_file(filename)

    linter = Linter(source, filename)
    issues = linter.run()

    if not issues:
        print(f"  {filename}: no issues found")
        return

    counts = {}

    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1

    print(f"  Analyzing {filename}")

    for issue in issues:
        location = f"{filename}:{issue['line']}:{issue['column']}"
        marker = "ERROR" if issue["severity"] == "error" else issue["code"]
        print(f"  {location}  {marker}  {issue['message']}")

    summary = ", ".join(
        f"{count} {severity}"
        for severity, count in sorted(counts.items())
    )

    print(f"  {summary} found")


def main():

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == "help":
        print_help()
        return

    if command == "version":
        print_version()
        return

    if command == "install":
        try:
            if len(sys.argv) == 3:
                install_package(sys.argv[2])
            elif len(sys.argv) == 2:
                install_all()
            else:
                print("Usage: wiz install [owner/repo[@tag]]")
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if command == "uninstall":
        if len(sys.argv) != 3:
            print("Usage: wiz uninstall <package>")
            return
        try:
            uninstall_package(sys.argv[2])
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if command == "update":
        try:
            if len(sys.argv) == 3:
                update_package(sys.argv[2])
            elif len(sys.argv) == 2:
                update_all()
            else:
                print("Usage: wiz update [package]")
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if command in ("-U", "update-self", "upgrade"):
        check_only = len(sys.argv) == 3 and sys.argv[2] in (
            "--check", "-c", "check"
        )

        try:
            update_self(check_only)
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)

        return

    if command == "list":
        try:
            list_packages()
        except WizError as error:
            print(f"Error: {error.message}")
            sys.exit(1)
        return

    if len(sys.argv) != 3:
        print("Missing wiz command argument")
        return

    filename = sys.argv[2]

    if command == "run":
        run(filename)

    elif command == "tokens":
        print_tokens(filename)

    elif command == "ast":
        print_ast(filename)

    elif command == "lint":
        lint(filename)

    else:
        print(f"Unknown command '{command}'")
        print("Type 'wiz help'")


if __name__ == "__main__":
    main()