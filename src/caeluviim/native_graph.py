from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import socket
import subprocess
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NEO4J_VERSION = "2026.06.0"
NEO4J_ARCHIVE = f"neo4j-community-{NEO4J_VERSION}-unix.tar.gz"
NEO4J_URL = f"https://dist.neo4j.org/{NEO4J_ARCHIVE}"
NEO4J_SHA256 = "1dcf62e7e8035e71732b86532b9f8e3219ce8956bd06940d5a0024696727192a"

JAVA_RELEASE = "jdk-21.0.12+8"
JAVA_DIRECTORY = "jdk-21.0.12+8-jre"
JAVA_ARCHIVE = "OpenJDK21U-jre_x64_linux_hotspot_21.0.12_8.tar.gz"
JAVA_URL = (
    "https://github.com/adoptium/temurin21-binaries/releases/download/"
    "jdk-21.0.12%2B8/" + JAVA_ARCHIVE
)
JAVA_SHA256 = "8a379a67c91a3ae61ffb33d46e0a40c7ba35e70713c4db31cfca30492f792eff"


class NativeGraphError(RuntimeError):
    pass


@dataclass(frozen=True)
class NativeGraphPaths:
    root: Path
    runtime: Path
    instance: Path
    neo4j_home: Path
    java_home: Path
    credentials: Path


class NativeNeo4j:
    """Repository-managed, non-root Neo4j Community installation."""

    def __init__(self, root: Path | str | None = None):
        root_path = Path(root or Path.home() / ".local" / "share" / "caeluviim")
        runtime = root_path / "runtime"
        instance = root_path / "neo4j"
        self.paths = NativeGraphPaths(
            root=root_path,
            runtime=runtime,
            instance=instance,
            neo4j_home=runtime / f"neo4j-community-{NEO4J_VERSION}",
            java_home=runtime / JAVA_DIRECTORY,
            credentials=instance / "credentials.json",
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _download(url: str, output: Path, expected_sha256: str) -> None:
        request = urllib.request.Request(
            url, headers={"User-Agent": "Caeluviim-Native-Installer/0.1"}
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            with output.open("wb") as handle:
                shutil.copyfileobj(response, handle, length=1024 * 1024)
        actual = NativeNeo4j._sha256(output)
        if actual != expected_sha256:
            output.unlink(missing_ok=True)
            raise NativeGraphError(
                f"checksum mismatch for {output.name}: {actual}"
            )

    @staticmethod
    def _safe_extract(archive: Path, destination: Path) -> None:
        destination = destination.resolve()
        with tarfile.open(archive, "r:gz") as package:
            for member in package.getmembers():
                target = (destination / member.name).resolve()
                if destination not in target.parents and target != destination:
                    raise NativeGraphError(
                        f"archive member escapes installation root: {member.name}"
                    )
            package.extractall(destination)

    def _credentials(self, *, create: bool) -> dict[str, str]:
        path = self.paths.credentials
        if path.exists():
            value = json.loads(path.read_text("utf-8"))
            if set(value) != {"user", "password"}:
                raise NativeGraphError("native Neo4j credentials file is invalid")
            return value
        if not create:
            raise NativeGraphError("native Neo4j credentials are not initialized")
        path.parent.mkdir(parents=True, exist_ok=True)
        value = {"user": "neo4j", "password": secrets.token_urlsafe(32)}
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, 0o600)
        return value

    def credentials(self) -> tuple[str, str]:
        value = self._credentials(create=False)
        return value["user"], value["password"]

    def environment(self) -> dict[str, str]:
        paths = self.paths
        env = dict(os.environ)
        env.update(
            {
                "JAVA_HOME": str(paths.java_home),
                "PATH": str(paths.java_home / "bin") + os.pathsep + env.get("PATH", ""),
                "NEO4J_HOME": str(paths.neo4j_home),
                "NEO4J_CONF": str(paths.instance / "conf"),
            }
        )
        return env

    def _neo4j(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        executable = self.paths.neo4j_home / "bin" / "neo4j"
        if not executable.exists():
            raise NativeGraphError("native Neo4j is not installed")
        return subprocess.run(
            [str(executable), *arguments],
            env=self.environment(),
            capture_output=True,
            text=True,
            check=check,
        )

    def install(self) -> dict[str, Any]:
        paths = self.paths
        paths.runtime.mkdir(parents=True, exist_ok=True)
        paths.instance.mkdir(parents=True, exist_ok=True)
        for child in ("data", "logs", "run", "import", "transactions"):
            (paths.instance / child).mkdir(parents=True, exist_ok=True)

        installed_now: list[str] = []
        with tempfile.TemporaryDirectory(prefix="caeluviim-graph-install-") as temporary:
            temporary_path = Path(temporary)
            if not (paths.java_home / "bin" / "java").exists():
                archive = temporary_path / JAVA_ARCHIVE
                self._download(JAVA_URL, archive, JAVA_SHA256)
                self._safe_extract(archive, paths.runtime)
                installed_now.append("java")
            if not (paths.neo4j_home / "bin" / "neo4j").exists():
                archive = temporary_path / NEO4J_ARCHIVE
                self._download(NEO4J_URL, archive, NEO4J_SHA256)
                self._safe_extract(archive, paths.runtime)
                installed_now.append("neo4j")

        config_directory = paths.instance / "conf"
        config_directory.mkdir(parents=True, exist_ok=True)
        config = "\n".join(
            [
                "# Managed by Caeluviim NativeNeo4j.",
                "server.default_listen_address=127.0.0.1",
                "server.default_advertised_address=127.0.0.1",
                f"server.directories.data={paths.instance / 'data'}",
                f"server.directories.logs={paths.instance / 'logs'}",
                f"server.directories.run={paths.instance / 'run'}",
                f"server.directories.import={paths.instance / 'import'}",
                "server.directories.plugins="
                + str(paths.neo4j_home / "plugins"),
                "server.directories.licenses="
                + str(paths.neo4j_home / "licenses"),
                "server.directories.transaction.logs.root="
                + str(paths.instance / "transactions"),
                "server.memory.heap.initial_size=512m",
                "server.memory.heap.max_size=1g",
                "server.memory.pagecache.size=512m",
                "dbms.usage_report.enabled=false",
                "",
            ]
        )
        config_path = config_directory / "neo4j.conf"
        if config_path.exists() and config_path.read_text("utf-8") != config:
            previous = config_path.read_bytes()
            previous_hash = hashlib.sha256(previous).hexdigest()
            history = config_directory / "history"
            history.mkdir(parents=True, exist_ok=True)
            historical_path = history / f"neo4j.{previous_hash}.conf"
            if not historical_path.exists():
                historical_path.write_bytes(previous)
        if not config_path.exists() or config_path.read_text("utf-8") != config:
            config_path.write_text(config, encoding="utf-8")

        credentials = self._credentials(create=True)
        auth_file = paths.instance / "data" / "dbms" / "auth.ini"
        databases = paths.instance / "data" / "databases"
        if not auth_file.exists() and not databases.exists():
            admin = paths.neo4j_home / "bin" / "neo4j-admin"
            result = subprocess.run(
                [
                    str(admin),
                    "dbms",
                    "set-initial-password",
                    credentials["password"],
                    "--require-password-change=false",
                ],
                env=self.environment(),
                capture_output=True,
                text=True,
                check=True,
            )
            password_status = result.stdout.strip() or "initialized"
        else:
            password_status = "preserved"

        java = subprocess.run(
            [str(paths.java_home / "bin" / "java"), "-version"],
            capture_output=True,
            text=True,
            check=True,
        )
        neo4j = self._neo4j("version")
        return {
            "root": str(paths.root),
            "installed_now": installed_now,
            "java": java.stderr.splitlines()[0],
            "neo4j": neo4j.stdout.strip(),
            "password_status": password_status,
            "credentials_file": str(paths.credentials),
            "credentials_mode": oct(paths.credentials.stat().st_mode & 0o777),
        }

    def start(self) -> dict[str, Any]:
        self.install()
        status = self.status()
        if status["running"]:
            return {"started_now": False, **status}
        log_path = self.paths.instance / "logs" / "console.log"
        with log_path.open("ab") as log:
            process = subprocess.Popen(
                [str(self.paths.neo4j_home / "bin" / "neo4j"), "console"],
                env=self.environment(),
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        import time

        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if process.poll() is not None:
                tail = log_path.read_text("utf-8", errors="replace")[-8000:]
                raise NativeGraphError(
                    f"Neo4j exited during startup with {process.returncode}:\n{tail}"
                )
            try:
                with socket.create_connection(("127.0.0.1", 7687), timeout=1):
                    return {
                        "started_now": True,
                        "pid": process.pid,
                        "console_log": str(log_path),
                        **self.status(),
                    }
            except OSError:
                time.sleep(1)
        raise NativeGraphError(
            f"Neo4j did not open Bolt within 120 seconds; inspect {log_path}"
        )

    def stop(self) -> dict[str, Any]:
        result = self._neo4j("stop", check=False)
        return {
            "command_exit_code": result.returncode,
            "output": (result.stdout + result.stderr).strip(),
            **self.status(),
        }

    def status(self) -> dict[str, Any]:
        result = self._neo4j("status", check=False)
        try:
            with socket.create_connection(("127.0.0.1", 7687), timeout=1):
                bolt_ready = True
        except OSError:
            bolt_ready = False
        return {
            "running": result.returncode == 0 and bolt_ready,
            "bolt_ready": bolt_ready,
            "status_exit_code": result.returncode,
            "status_output": (result.stdout + result.stderr).strip(),
            "http_uri": "http://127.0.0.1:7474",
            "bolt_uri": "bolt://127.0.0.1:7687",
            "root": str(self.paths.root),
        }
