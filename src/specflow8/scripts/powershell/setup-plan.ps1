param(
    [string]$Root = ".",
    [string]$FeatureId = "",
    [switch]$Json
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$resolvedRoot = (Resolve-Path $Root).Path
$specflow8 = Get-Specflow8Command

Push-Location $resolvedRoot
try {
    & $specflow8 check | Out-Null

    $effectiveFeatureId = if ($FeatureId -ne "") { $FeatureId } else { Resolve-LatestFeatureId -ReadmePath ".\README.md" }
    if (-not $effectiveFeatureId) {
        throw "No feature id found. Run 'specflow8 specify' first or pass -FeatureId."
    }

    $required = @("README.md", "DOMAIN.md", "PLAN.md", "ARCHITECTURE.md")
    $missing = @($required | Where-Object { -not (Test-Path $_) })
    if ($missing.Count -gt 0) {
        throw ("Missing required docs: " + ($missing -join ", "))
    }
}
finally {
    Pop-Location
}

$result = [ordered]@{
    FEATURE_ID = $effectiveFeatureId
    ROOT = $resolvedRoot
    AVAILABLE_DOCS = @("README.md", "DOMAIN.md", "PLAN.md", "ARCHITECTURE.md")
    UPDATED_TARGETS = @("ARCHITECTURE.md", "PLAN.md")
}

if ($Json) {
    $result | ConvertTo-Json -Depth 5
}
else {
    Write-Host "Feature: $effectiveFeatureId"
    Write-Host "Plan context ready: README.md, DOMAIN.md, PLAN.md, ARCHITECTURE.md"
}

