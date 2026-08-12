<#
.SYNOPSIS
    Scaffold a new module from the bundled module template.

.DESCRIPTION
    Copies module_template.py from this repo's templates
    (src/scriptkit/templates) into the target directory, names it snake_case,
    and reports the path. Modules carry no dependency pin — they import
    scriptkit directly. This is the local-dev companion to the cross-platform
    `scriptkit new` command.

.PARAMETER Name
    Name for the new module; punctuation is normalized to snake_case and a .py
    extension is added (e.g. "Cache Utils" -> cache_utils.py).

.PARAMETER Dir
    Directory to create the module in (default: src/scriptkit).

.PARAMETER Force
    Overwrite an existing file of the same name.

.EXAMPLE
    .\new-module.ps1 cache_utils
    .\new-module.ps1 "Time Helpers" -Dir src/scriptkit
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Name,
    [string]$Dir = "src/scriptkit",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Normalize to a snake_case .py filename.
$stem = ($Name -replace '\.py$', '' -replace '[^A-Za-z0-9]+', '_').Trim('_').ToLower()
if (-not $stem) { throw "Could not derive a filename from '$Name'." }

$template = Join-Path $PSScriptRoot "src\scriptkit\templates\module_template.py"
if (-not (Test-Path $template)) { throw "Module template not found at $template." }

$destDir = Join-Path $PSScriptRoot $Dir
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
$dest = Join-Path $destDir "$stem.py"
if ((Test-Path $dest) -and -not $Force) {
    throw "Refusing to overwrite $dest (pass -Force to replace it)."
}

# Read/write as UTF-8 without BOM. Windows PowerShell 5.1 defaults to the ANSI
# codepage and would corrupt the box-drawing separators in the template.
$content = [System.IO.File]::ReadAllText($template)
[System.IO.File]::WriteAllText($dest, $content, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Created $Dir/$stem.py"
Write-Host "Next:  edit $Dir/$stem.py and fill in the module."
