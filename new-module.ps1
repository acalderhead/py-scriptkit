<#
.SYNOPSIS
    Scaffold a new module from the bundled module template.

.DESCRIPTION
    Copies module_template.py from this repo's templates into the target
    directory. With -Name it writes directly; with no -Name (e.g. the
    double-click .bat) it prompts, and on a name collision it explains and
    re-prompts rather than overwriting.

.PARAMETER Name
    Optional. Normalized to a snake_case filename (e.g. "Cache Utils" ->
    cache_utils.py). Omit for the interactive prompt.

.PARAMETER Dir
    Directory to create the module in (default: src/scriptkit).

.PARAMETER Force
    Overwrite an existing file (honored only with -Name).

.EXAMPLE
    .\new-module.ps1               # interactive
    .\new-module.ps1 cache_utils
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Name,
    [string]$Dir = "src/scriptkit",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$template = Join-Path $PSScriptRoot "src\scriptkit\templates\module_template.py"
$destDir  = Join-Path $PSScriptRoot $Dir

# Normalize to a snake_case stem.
function Get-Stem([string]$raw) {
    ($raw -replace '\.py$', '' -replace '[^A-Za-z0-9]+', '_').Trim('_').ToLower()
}

$stem = $null

if ($Name) {
    $stem = Get-Stem $Name
    if (-not $stem) { throw "Could not derive a filename from '$Name'." }
    $dest = Join-Path $destDir "$stem.py"
    if ((Test-Path $dest) -and -not $Force) {
        throw "Refusing to overwrite $dest (pass -Force to replace it)."
    }
} else {
    while (-not $stem) {
        $raw = Read-Host "Name for the new module"
        $candidateStem = Get-Stem $raw
        if (-not $candidateStem) { Write-Host "  Please enter a valid name."; continue }
        $dest = Join-Path $destDir "$candidateStem.py"
        if (Test-Path $dest) {
            Write-Host "  $candidateStem.py already exists in $Dir; choose a different name."
            continue
        }
        $stem = $candidateStem
    }
}

if (-not (Test-Path $template)) { throw "Module template not found at $template." }
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }

# Read/write as UTF-8 without BOM. Windows PowerShell 5.1 defaults to the ANSI
# codepage and would corrupt the box-drawing separators in the template.
$content = [System.IO.File]::ReadAllText($template)
[System.IO.File]::WriteAllText($dest, $content, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Created $Dir/$stem.py"
Write-Host "Next:  edit $Dir/$stem.py and fill in the module."
