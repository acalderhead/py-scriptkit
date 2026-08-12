<#
.SYNOPSIS
    Scaffold a new pytest file from the bundled test template.

.DESCRIPTION
    With -Name, creates tests/test_<name>.py directly. With no -Name (e.g. the
    double-click .bat), runs interactively: pick an existing script/module file
    to test, or name a brand-new test file. On a name collision it explains and
    re-prompts rather than overwriting.

.PARAMETER Name
    Optional. Module under test; a leading "test_" is stripped and then re-added
    (e.g. "settings" -> test_settings.py). Omit for the interactive flow.

.PARAMETER Force
    Overwrite an existing file (honored only with -Name).

.EXAMPLE
    .\new-test.ps1                 # interactive
    .\new-test.ps1 settings        # -> tests/test_settings.py
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Name,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$testsDir = Join-Path $PSScriptRoot "tests"
$template = Join-Path $PSScriptRoot "src\scriptkit\templates\test_template.py"

# Normalize to a snake_case stem; drop any leading "test_" so it is added once.
function Get-TestStem([string]$raw) {
    ($raw -replace '\.py$', '' -replace '^test_', '' -replace '[^A-Za-z0-9]+', '_').Trim('_').ToLower()
}

# Existing script/module files that could be tested (recurses scripts\ + src\).
function Find-SourceFiles {
    $files = @()
    foreach ($dir in @("scripts", "src")) {
        $root = Join-Path $PSScriptRoot $dir
        if (Test-Path $root) {
            $found = Get-ChildItem $root -Recurse -File -Filter *.py
            $files += $found | Where-Object { $_.Name -notlike "test_*" -and $_.Name -ne "__init__.py" -and $_.FullName -notmatch '[\\/](tests|templates)[\\/]' }
        }
    }
    $files | Sort-Object Name
}

$stem = $null

if ($Name) {
    $stem = Get-TestStem $Name
    if (-not $stem) { throw "Could not derive a filename from '$Name'." }
    $dest = Join-Path $testsDir "test_$stem.py"
    if ((Test-Path $dest) -and -not $Force) {
        throw "Refusing to overwrite $dest (pass -Force to replace it)."
    }
} else {
    $answer = Read-Host "Create a test for an EXISTING script/module file? [y/N]"
    if ($answer -match '^\s*[Yy]') {
        $candidates = @(Find-SourceFiles)
        if ($candidates.Count -eq 0) {
            Write-Host "No source files found under scripts\ or src\; name a new test instead."
        } else {
            while (-not $stem) {
                Write-Host ""
                Write-Host "Select a file to create a test for:"
                for ($i = 0; $i -lt $candidates.Count; $i++) {
                    Write-Host ("  [{0}] {1}" -f ($i + 1), $candidates[$i].Name)
                }
                $pick = Read-Host "Number (blank to cancel)"
                if ([string]::IsNullOrWhiteSpace($pick)) { Write-Host "Cancelled."; return }
                $index = 0
                if (-not [int]::TryParse($pick, [ref] $index) -or $index -lt 1 -or $index -gt $candidates.Count) {
                    Write-Host "  '$pick' is not a valid choice; try again."
                    continue
                }
                $candidateStem = Get-TestStem $candidates[$index - 1].BaseName
                $dest = Join-Path $testsDir "test_$candidateStem.py"
                if (Test-Path $dest) {
                    Write-Host "  A test already exists for that file (tests\test_$candidateStem.py); pick another."
                    continue
                }
                $stem = $candidateStem
            }
        }
    }

    if (-not $stem) {
        Write-Host ""
        Write-Host "Note: 'test_' is prepended to the name, e.g. 'foo' -> test_foo.py."
        while (-not $stem) {
            $raw = Read-Host "Name for the new test"
            $candidateStem = Get-TestStem $raw
            if (-not $candidateStem) { Write-Host "  Please enter a valid name."; continue }
            $dest = Join-Path $testsDir "test_$candidateStem.py"
            if (Test-Path $dest) {
                Write-Host "  test_$candidateStem.py already exists; choose a different name."
                continue
            }
            $stem = $candidateStem
        }
    }
}

if (-not (Test-Path $template)) { throw "Test template not found at $template." }
if (-not (Test-Path $testsDir)) { New-Item -ItemType Directory -Path $testsDir | Out-Null }

# Read/write as UTF-8 without BOM (matches the box-drawing separators safely).
$content = [System.IO.File]::ReadAllText($template)
[System.IO.File]::WriteAllText($dest, $content, (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "Created tests/test_$stem.py"
Write-Host "Next:  edit tests/test_$stem.py and write the tests."
