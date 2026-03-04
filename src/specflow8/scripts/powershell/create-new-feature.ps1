param(
    [string]$Root = ".",
    [Parameter(Mandatory = $true)]
    [string]$Description,
    [string]$Tech = "",
    [switch]$WithTests,
    [string]$FeatureId = "",
    [switch]$Json
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$resolvedRoot = (Resolve-Path $Root).Path
$specflow8 = Get-Specflow8Command

Push-Location $resolvedRoot
try {
    $specifyArgs = @("specify", $Description)
    if ($FeatureId -ne "") {
        $specifyArgs += @("--id", $FeatureId)
    }
    $specifyOut = & $specflow8 @specifyArgs
    $specifyOut | Out-Host

    $fromOutput = $null
    foreach ($line in $specifyOut) {
        if ($line -match "Feature specified:\s*(F-\d{3})") {
            $fromOutput = $Matches[1]
            break
        }
    }
    $effectiveFeatureId = if ($FeatureId -ne "") { $FeatureId } elseif ($fromOutput) { $fromOutput } else { Resolve-LatestFeatureId -ReadmePath ".\README.md" }
    if (-not $effectiveFeatureId) {
        throw "Unable to detect feature id from README.md."
    }

    if ($Tech -ne "") {
        & $specflow8 "plan" "--feature" $effectiveFeatureId $Tech | Out-Host
        $taskArgs = @("tasks", "--feature", $effectiveFeatureId)
        if ($WithTests) {
            $taskArgs += "--with-tests"
        }
        & $specflow8 @taskArgs | Out-Host
    }
}
finally {
    Pop-Location
}

$result = [ordered]@{
    FEATURE_ID = $effectiveFeatureId
    ROOT = $resolvedRoot
    UPDATED = @("README.md", "DOMAIN.md", "PLAN.md")
    WITH_PLAN = [bool]($Tech -ne "")
    WITH_TASKS = [bool]($Tech -ne "")
}

if ($Json) {
    $result | ConvertTo-Json -Depth 5
}
else {
    Write-Host "Feature pipeline complete: $effectiveFeatureId"
}

