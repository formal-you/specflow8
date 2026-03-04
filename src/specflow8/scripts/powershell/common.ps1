Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-Specflow8Command {
    $cmd = Get-Command specflow8 -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "specflow8 command not found in PATH."
    }
    return $cmd.Source
}

function Resolve-LatestFeatureId {
    param(
        [string]$ReadmePath = ".\README.md"
    )
    if (-not (Test-Path $ReadmePath)) {
        return $null
    }
    $text = Get-Content -Raw -Encoding UTF8 $ReadmePath
    $matches = [regex]::Matches($text, "<!-- specflow8:feature:(F-\d{3}):start -->")
    if ($matches.Count -eq 0) {
        return $null
    }
    return $matches[$matches.Count - 1].Groups[1].Value
}

