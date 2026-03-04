param(
    [string]$Root = ".",
    [string]$FeatureId = "",
    [switch]$IncludeTasks,
    [switch]$RequireTasks,
    [switch]$Json
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptDir "common.ps1")

$resolvedRoot = (Resolve-Path $Root).Path
$specflow8 = Get-Specflow8Command

Push-Location $resolvedRoot
try {
    & $specflow8 check | Out-Null
}
finally {
    Pop-Location
}

$effectiveFeatureId = if ($FeatureId -ne "") { $FeatureId } else {
    Resolve-LatestFeatureId -ReadmePath (Join-Path $resolvedRoot "README.md")
}

$coreDocs = @(
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "DOMAIN.md",
    "STATE.md",
    "PLAN.md",
    "TASKS.md",
    "DECISIONS.md"
)
$missingDocs = @($coreDocs | Where-Object { -not (Test-Path (Join-Path $resolvedRoot $_)) })
$availableDocs = @($coreDocs | Where-Object { Test-Path (Join-Path $resolvedRoot $_) })

$warnings = [System.Collections.Generic.List[string]]::new()
$errors = [System.Collections.Generic.List[string]]::new()

if (-not $effectiveFeatureId) {
    $warnings.Add("No feature id resolved from README.md.")
}
else {
    $readmePath = Join-Path $resolvedRoot "README.md"
    if (-not (Test-Path $readmePath)) {
        $errors.Add("README.md is missing.")
    }
    else {
        $readmeText = Get-Content -Raw -Encoding UTF8 $readmePath
        $marker = "<!-- specflow8:feature:" + $effectiveFeatureId + ":start -->"
        if ($readmeText -notmatch [regex]::Escape($marker)) {
            $errors.Add("Feature block not found in README.md: $effectiveFeatureId")
        }
    }
}

$taskTotal = 0
$taskDone = 0
$taskPending = 0

if (($IncludeTasks -or $RequireTasks) -and $effectiveFeatureId) {
    $tasksPath = Join-Path $resolvedRoot "TASKS.md"
    if (Test-Path $tasksPath) {
        $tasksText = Get-Content -Raw -Encoding UTF8 $tasksPath
        $escaped = [regex]::Escape($effectiveFeatureId)
        $pattern = "(?s)<!-- specflow8:feature:" + $escaped + ":start -->\r?\n(.*?)\r?\n<!-- specflow8:feature:" + $escaped + ":end -->"
        $block = [regex]::Match($tasksText, $pattern)
        if ($block.Success) {
            $statusMatches = [regex]::Matches($block.Groups[1].Value, "^\|\s*T-\d{3}\s*\|\s*(?:.*?\|\s*){1,2}P[0-2]\s*\|\s*(todo|in_progress|done|blocked)\s*\|\s*.*?\|", [System.Text.RegularExpressions.RegexOptions]::Multiline)
            $taskTotal = $statusMatches.Count
            foreach ($match in $statusMatches) {
                if ($match.Groups[1].Value -eq "done") {
                    $taskDone++
                }
            }
            $taskPending = $taskTotal - $taskDone
        }
        elseif ($RequireTasks) {
            $errors.Add("Task block not found in TASKS.md: $effectiveFeatureId")
        }
    }
}

if ($RequireTasks -and $taskTotal -eq 0) {
    $errors.Add("No tasks found while -RequireTasks is set.")
}
if ($missingDocs.Count -gt 0) {
    $errors.Add("Missing core docs: " + ($missingDocs -join ", "))
}

$ok = $errors.Count -eq 0
$result = [ordered]@{
    ROOT = $resolvedRoot
    FEATURE_ID = if ($effectiveFeatureId) { $effectiveFeatureId } else { $null }
    AVAILABLE_DOCS = $availableDocs
    MISSING_DOCS = $missingDocs
    TASKS = [ordered]@{
        total = $taskTotal
        done = $taskDone
        pending = $taskPending
    }
    INCLUDE_TASKS = [bool]$IncludeTasks
    REQUIRE_TASKS = [bool]$RequireTasks
    WARNINGS = @($warnings)
    ERRORS = @($errors)
    OK = $ok
}

if ($Json) {
    $result | ConvertTo-Json -Depth 6
}
else {
    Write-Host "Root: $resolvedRoot"
    Write-Host ("Feature: " + ($(if ($effectiveFeatureId) { $effectiveFeatureId } else { "N/A" })))
    Write-Host ("Core docs missing: " + $missingDocs.Count)
    if ($IncludeTasks -or $RequireTasks) {
        Write-Host ("Tasks: total=$taskTotal done=$taskDone pending=$taskPending")
    }
    foreach ($w in $warnings) {
        Write-Host "WARNING: $w"
    }
    foreach ($e in $errors) {
        Write-Host "ERROR: $e"
    }
    Write-Host "OK: $ok"
}

if (-not $ok) {
    exit 1
}
