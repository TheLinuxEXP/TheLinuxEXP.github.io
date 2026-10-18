"""Live preview (jekyll serve) and publishing (git commit + push)."""

import atexit
import os
import shutil
import signal
import subprocess
from pathlib import Path

PREVIEW_HOST = "127.0.0.1"  # never anything else: the preview is for this laptop only


class PublishError(Exception):
    pass


def _git(root: Path, *args: str, timeout: int = 120):
    if shutil.which("git") is None:
        raise PublishError("git is not installed.")
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}  # never hang on a password prompt
    result = subprocess.run(
        ["git", *args], cwd=root, env=env, capture_output=True, text=True, timeout=timeout, check=False,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def changed_files(root: Path) -> list:
    code, out = _git(root, "status", "--porcelain", "-uall")
    if code != 0:
        raise PublishError(f"git status failed: {out}")
    return [line for line in out.splitlines() if line.strip()]


def commit_and_push(root: Path, message: str, push: bool) -> str:
    message = " ".join(message.split())
    if not message or len(message) > 200:
        raise PublishError("Write a short description of the change (200 characters at most).")
    log = []
    for args in (("add", "-A"), ("commit", "-m", message)):
        code, out = _git(root, *args)
        log.append(f"$ git {args[0]}\n{out}")
        if code != 0:
            raise PublishError("\n".join(log))
    if push:
        code, out = _git(root, "push")
        log.append(f"$ git push\n{out}")
        if code != 0:
            raise PublishError("\n".join(log) + "\n\nThe commit is saved locally; fix the problem above and push again from a terminal.")
    return "\n".join(log)


class Preview:
    """Runs `jekyll serve` bound to 127.0.0.1 so you can look at the site before publishing."""

    def __init__(self, root: Path, log_path: Path, port: int = 4000):
        self.root, self.log_path, self.port = root, log_path, port
        self.proc = None
        atexit.register(self.stop)

    @property
    def url(self) -> str:
        return f"http://{PREVIEW_HOST}:{self.port}/"

    def running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def start(self) -> None:
        if self.running():
            return
        if shutil.which("bundle") is None:
            raise PublishError("Ruby's `bundle` command was not found. Install Ruby, then run `bundle install` in the site folder.")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        log = open(self.log_path, "wb")
        self.proc = subprocess.Popen(
            ["bundle", "exec", "jekyll", "serve", "--host", PREVIEW_HOST, "--port", str(self.port)],
            cwd=self.root, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            env={**os.environ, "JEKYLL_ENV": "development"},
        )

    def stop(self) -> None:
        if self.running():
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
        self.proc = None

    def log_tail(self, lines: int = 25) -> str:
        if not self.log_path.is_file():
            return ""
        return "\n".join(self.log_path.read_text(errors="replace").splitlines()[-lines:])
