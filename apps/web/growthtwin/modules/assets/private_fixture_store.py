"""Fresh private temporary files for generated fixtures only, never user storage.

No supplied roots, filenames, traversal, public URL or recursive cleanup. Native
checks reduce accidental exposure; they do not defend against a hostile process
already running as the same OS user or provide a production storage sandbox.
"""

import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4


def _private_windows(path):
    script = r"""
$ErrorActionPreference='Stop'
try {
  Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop
  Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop
  $path=[Console]::In.ReadToEnd() | ConvertFrom-Json
  $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  $acl=Get-Acl -LiteralPath $path
  if($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid){throw 'Owner'}
  & "$env:SystemRoot/System32/icacls.exe" $path /reset | Out-Null
  if($LASTEXITCODE){throw 'ACL reset'}
  & "$env:SystemRoot/System32/icacls.exe" $path /inheritance:r /grant:r ('*'+$sid+':(OI)(CI)F') | Out-Null
  if($LASTEXITCODE){throw 'ACL'}
  $acl=Get-Acl -LiteralPath $path
  if(-not $acl.AreAccessRulesProtected){throw 'Inheritance'}
  $rules=@($acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
  if($rules.Count -eq 0){throw 'Rules'}
  foreach($rule in $rules){
    if($rule.IdentityReference.Value -ne $sid -or $rule.AccessControlType -ne 'Allow'){throw 'Principal'}
  }
  [Console]::Out.Write('private')
} catch {exit 1}
"""
    executable = (
        Path(os.environ["SystemRoot"])
        / "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    result = subprocess.run(
        [
            str(executable),
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ],
        input=json.dumps(str(path)),
        text=True,
        capture_output=True,
        timeout=20,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode or result.stdout != "private":
        raise ValueError("Private fixture storage unavailable.")


class PrivateFixtureStore:
    """An inventoried disposable directory with a maximum of six bounded files."""

    def __enter__(self):
        self._root = Path(tempfile.mkdtemp(prefix="yaparo-raster-fixture-"))
        self._files = {}
        try:
            if os.name == "nt":
                _private_windows(self._root)
            else:
                self._root.chmod(0o700)
            self._identity = self._root.stat().st_dev, self._root.stat().st_ino
            self._check_root()
        except Exception:
            self._root.rmdir()  # Empty only; never delete an unknown tree.
            raise
        return self

    def _check_root(self):
        info = self._root.stat(follow_symlinks=False)
        if (
            not stat.S_ISDIR(info.st_mode)
            or stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT
            or (info.st_dev, info.st_ino) != self._identity
            or (os.name != "nt" and stat.S_IMODE(info.st_mode) != 0o700)
        ):
            raise ValueError("Fixture root changed.")

    def put(self, data):
        self._check_root()
        if type(data) is not bytes or not 1 <= len(data) <= 8 * 1024 * 1024:
            raise ValueError("Fixture bytes refused.")
        if len(self._files) >= 6:
            raise ValueError("Fixture file quota reached.")
        key = uuid4()
        path = self._root / key.hex
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
        self._files[key] = path
        with os.fdopen(descriptor, "wb") as target:
            target.write(data)
            target.flush()
            os.fsync(target.fileno())
        return key

    def read(self, key):
        self._check_root()
        path = self._files[key]
        info = path.stat(follow_symlinks=False)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or getattr(info, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("Fixture file changed.")
        with path.open("rb") as source:
            value = source.read(8 * 1024 * 1024 + 1)
        if len(value) > 8 * 1024 * 1024:
            raise ValueError("Fixture file too large.")
        return value

    def __exit__(self, *exception):
        self._check_root()
        if set(self._root.iterdir()) != set(self._files.values()):
            raise ValueError("Unknown fixture file prevents cleanup.")
        for key, path in self._files.items():
            self.read(key)  # Refuse replaced links before removing exact files.
            path.unlink()
        self._root.rmdir()
        return False
