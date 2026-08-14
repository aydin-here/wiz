import importlib.util
import os
import sys

from package import (
    MANIFEST_FILE,
    WIZ_ENTRY_FILE,
    PYTHON_ENTRY_FILE,
    load_manifest,
    package_type,
    entry_file,
    is_python_package,
    check_wiz_version,
)
from package_manager import packages_dir
from runtime import NativeModule
from errors import (
    InvalidPackageManifestError,
    PythonDependencyError,
    PythonPackageLoadError,
)


class PackageResolution:

    """Describes how an imported module was resolved."""

    def __init__(
        self,
        module,
        kind,
        entry=None,
        directory=None,
        manifest=None,
        manifest_path=None,
    ):
        self.module = module
        self.kind = kind            # "local", "wiz" or "python"
        self.entry = entry          # entry file (main.wiz / main.py / module.wiz)
        self.directory = directory  # package directory when applicable
        self.manifest = manifest    # validated manifest dict when present
        self.manifest_path = manifest_path


class PackageLoader:

    """Locates and loads external Wiz packages.

    Installed packages are stored in a global store (~/.wiz/packages by
    default, overridable with WIZ_HOME) and are therefore available to
    every project. The loader also resolves project-local modules (a
    ``<module>.wiz`` file next to the running program). Built-in stdlib
    modules are resolved by the interpreter before this loader is
    consulted, so external packages can never shadow them.
    """

    def __init__(self, base_path="."):
        self.base_path = base_path

    def package_dir(self):
        return packages_dir()

    def find(self, module):
        """Resolve a module name to a PackageResolution, or None."""

        local = os.path.join(self.base_path, module + ".wiz")

        if os.path.isfile(local):
            return PackageResolution(module, "local", entry=local)

        flat = os.path.join(self.package_dir(), module + ".wiz")

        if os.path.isfile(flat):
            return PackageResolution(module, "wiz", entry=flat)

        directory = os.path.join(self.package_dir(), module)

        if os.path.isdir(directory):
            return self._resolve_package_directory(module, directory)

        return None

    def _resolve_package_directory(self, module, directory):

        manifest_file = os.path.join(directory, MANIFEST_FILE)

        if os.path.isfile(manifest_file):

            manifest = load_manifest(directory)

            check_wiz_version(manifest, path=manifest_file)

            pkg_type = package_type(manifest)

            if is_python_package(pkg_type):

                entry = os.path.join(directory, entry_file(manifest))

                if not os.path.isfile(entry):
                    raise InvalidPackageManifestError(
                        f"Python package '{module}' is missing its entry "
                        f"file '{entry_file(manifest)}' in '{directory}'",
                        path=manifest_file
                    )

                return PackageResolution(
                    module,
                    "python",
                    entry=entry,
                    directory=directory,
                    manifest=manifest,
                    manifest_path=manifest_file,
                )

            entry = os.path.join(directory, entry_file(manifest))

            if not os.path.isfile(entry):
                raise InvalidPackageManifestError(
                    f"Wiz package '{module}' is missing its entry "
                    f"file '{entry_file(manifest)}' in '{directory}'",
                    path=manifest_file
                )

            return PackageResolution(
                module,
                "wiz",
                entry=entry,
                directory=directory,
                manifest=manifest,
                manifest_path=manifest_file,
            )

        # Legacy layout without a manifest: a directory holding a module
        # named after the package (wiz_modules/<module>/<module>.wiz).
        legacy = os.path.join(directory, module + ".wiz")

        if os.path.isfile(legacy):
            return PackageResolution(module, "wiz", entry=legacy, directory=directory)

        raise InvalidPackageManifestError(
            f"Package '{module}' has no '{MANIFEST_FILE}' manifest and no "
            f"entry module in '{directory}'. Expected '{WIZ_ENTRY_FILE}' "
            f"for a Wiz package or '{PYTHON_ENTRY_FILE}' for a Python "
            f"package (or point 'entry' at the file in wiz.pkg).",
            path=directory
        )

    def load_python(self, resolution, interpreter=None):
        """Load a Python package entry point and wrap it as a NativeModule."""

        self._check_python_dependencies(resolution)

        module_name = f"_wiz_native_{resolution.module}"

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, resolution.entry
            )

            if spec is None or spec.loader is None:
                raise PythonPackageLoadError(
                    f"Could not create a loader for '{resolution.entry}'",
                    path=resolution.entry
                )

            python_module = importlib.util.module_from_spec(spec)

            # Make the package importable so the entry script can import
            # its own internal Python submodules, e.g. a main.py that does
            # `import wiz_tk`. Both the package directory and the entry
            # file's own directory are added; they are removed again once
            # the module has been executed.
            sys_path = list(sys.path)

            try:
                if resolution.directory:
                    sys.path.insert(0, resolution.directory)

                entry_dir = os.path.dirname(resolution.entry)

                if entry_dir and entry_dir != resolution.directory:
                    sys.path.insert(0, entry_dir)

                dont_write_bytecode = sys.dont_write_bytecode

                sys.dont_write_bytecode = True

                try:
                    spec.loader.exec_module(python_module)
                finally:
                    sys.dont_write_bytecode = dont_write_bytecode

            finally:
                sys.path[:] = sys_path

        except PythonDependencyError:
            raise

        except Exception as error:
            raise PythonPackageLoadError(
                f"Failed to load Python package '{resolution.module}' "
                f"from '{resolution.entry}': "
                f"{type(error).__name__}: {error}",
                path=resolution.entry
            ) from error

        package = getattr(python_module, "module", None)

        if package is None:
            raise PythonPackageLoadError(
                f"Python package '{resolution.module}' must define a "
                f"'module' object in '{resolution.entry}'",
                path=resolution.entry
            )

        native = NativeModule(resolution.module, package)

        if interpreter is not None:
            native.interpreter = interpreter

        return native

    def _check_python_dependencies(self, resolution):

        if not resolution.manifest:
            return

        dependencies = resolution.manifest.get("python_dependencies", {})

        missing = []

        for package_name in dependencies:

            try:
                spec = importlib.util.find_spec(package_name)
            except (ImportError, ValueError, AttributeError):
                spec = None

            if spec is None:
                missing.append(package_name)

        if missing:
            raise PythonDependencyError(
                f"Python package '{resolution.module}' requires the Python "
                f"module(s): {', '.join(missing)}. Install them with pip "
                "before importing the package.",
                path=resolution.manifest_path or resolution.directory
            )
