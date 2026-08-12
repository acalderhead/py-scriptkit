<#
.SYNOPSIS
    Scaffold a new pytest file from the bundled test template.

.DESCRIPTION
    Copies test_template.py from this repo's templates
    (src/scriptkit/templates) into tests/, named test_<name>.py.

.PARAMETER Name
    Name for the module under test; punctuation is normalized to snake_case and
    a leading "test_" is stripped, then re-added (e.g. "settings" ->
    test_settings.py).

.PARAMETER Force
    Overwrite an existing file of the same name.

.EXAMPLE
    .\new-test.ps1 settings
    .\new-test.ps1 test_cli -Force
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Name,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Normalize to a snake_case stem; drop any leading "test_" so it is added once.
$stem = ($Name -replace '\.py$', '' -replace '^test_', '' -replace '[^A-Za-z0-9]+', '_').Trim('_').ToLower()
if (-not $stem) { throw "Could not derive a filename from '$Name'." }

$template = Join-Path $PSScriptRoot "src\scriptkit\templates\test_template.py"
if (-not (Test-Path $template)) { throw "Test template not found at $template." }

$testsDir = Join-Path $PSScriptRoot "tests"
if (-not (Test-Path $testsDir)) { New-Item -ItemType Directory -Path $testsDir | Out-Null }
$dest = Join-Path $testsDir "test_$stem.py"
if ((Test-Path $dest) -and -not $Force) {
    throw "Refusing to overwrite $dest (pass -Force to replace it)."
}

# Read/write as UTF-8 without BOM (see new-module.ps1 for the codepage rationale).
$content = [System.IO.File]::ReadAllText($template)
[System.IO.File]::WriteAllText($dest, $content, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Created tests/test_$stem.py"
Write-Host "Next:  edit tests/test_$stem.py and write the tests."
