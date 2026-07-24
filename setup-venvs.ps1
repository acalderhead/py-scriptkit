<#
.SYNOPSIS
    Create (or recreate) the per-version dev virtualenvs used by VS Code.

.DESCRIPTION
    Installs uv-managed CPython 3.11 / 3.12 / 3.13, then builds one venv per
    supported minor version (.venv311 / .venv312 / .venv313), each an editable
    install of this package with its dev extras (".[dev]": pytest, ruff). VS Code
    uses these for IntelliSense, linting, and debugging (default: .venv313); the
    versioned "pytest" tasks run the suite on each interpreter so you can verify
    the package across every version it claims to support.

.PARAMETER Force
    Delete and recreate venvs that already exist.

.EXAMPLE
    .\setup-venvs.ps1
    .\setup-venvs.ps1 -Force
#>
[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$versions = "3.11", "3.12", "3.13"

# All three interpreters come from uv's reproducible standalone builds.
Write-Host "Installing uv-managed CPython $($versions -join ', ')..."
uv python install @versions

foreach ($v in $versions) {
    $name = ".venv" + ($v -replace '\.', '')
    $path = Join-Path $PSScriptRoot $name

    if (Test-Path $path) {
        if ($Force) {
            Write-Host "Removing existing $name..."
            Remove-Item -Recurse -Force $path
        } else {
            Write-Host "$name already exists (pass -Force to recreate); reinstalling editable package only."
        }
    }

    if (-not (Test-Path $path)) {
        Write-Host "Creating $name (Python $v, uv-managed)..."
        uv venv --python-preference only-managed --python $v $path
    }

    Write-Host "Installing editable .[dev] into $name..."
    uv pip install --python (Join-Path $path "Scripts\python.exe") -e ".[dev]"
}

Write-Host ""
Write-Host "Done. VS Code default interpreter: .venv313"
Write-Host "Run 'pytest (all versions)' (test task) to exercise the suite on 3.11/3.12/3.13."
