param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw "verify_godot_uids.ps1 requires PowerShell 7+ (pwsh). Windows PowerShell 5.1 lacks [System.IO.Path]::GetRelativePath."
}

$RepoRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$UidPattern = 'uid://[A-Za-z0-9_]+'
$Failures = New-Object System.Collections.Generic.List[string]
$OwnerEntries = New-Object System.Collections.Generic.List[object]
$OwnerUidByResourcePath = @{}

function Convert-ToResourcePath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $relativePath = [System.IO.Path]::GetRelativePath($RepoRoot, $fullPath)
    return "res://" + ($relativePath -replace '\\', '/')
}

function Add-Failure {
    param([string]$Message)

    $Failures.Add($Message) | Out-Null
}

function Add-OwnerEntry {
    param(
        [string]$Uid,
        [string]$OwnerPath,
        [string]$SourcePath,
        [int]$LineNumber
    )

    $OwnerEntries.Add(
        [pscustomobject]@{
            Uid = $Uid
            OwnerPath = $OwnerPath
            SourcePath = $SourcePath
            LineNumber = $LineNumber
        }
    ) | Out-Null

    if (-not $OwnerUidByResourcePath.ContainsKey($OwnerPath)) {
        $OwnerUidByResourcePath[$OwnerPath] = $Uid
    }
}

function Resolve-ImportOwnerPath {
    param(
        [string[]]$Lines,
        [string]$FallbackPath
    )

    foreach ($line in $Lines) {
        if ($line -match '^source_file="([^"]+)"') {
            return $Matches[1]
        }
    }

    return Convert-ToResourcePath $FallbackPath
}

function Get-ProjectFiles {
    param([string[]]$Extensions)

    Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force |
        Where-Object {
            $relativePath = [System.IO.Path]::GetRelativePath($RepoRoot, $_.FullName)
            $topSegment = ($relativePath -split '[\\/]')[0]
            $topSegment -notin @('.git', '.godot', 'build') -and
                $Extensions -contains $_.Extension
        }
}

foreach ($file in Get-ProjectFiles @('.tscn', '.tres', '.uid', '.import')) {
    $resourcePath = Convert-ToResourcePath $file.FullName
    $lines = @(Get-Content -LiteralPath $file.FullName -Encoding UTF8)

    if ($file.Extension -eq '.tscn' -and $lines.Count -gt 0) {
        $match = [regex]::Match($lines[0], '\[gd_scene[^\]]*uid="(' + $UidPattern + ')"')
        if ($match.Success) {
            Add-OwnerEntry $match.Groups[1].Value $resourcePath $resourcePath 1
        }
    } elseif ($file.Extension -eq '.tres' -and $lines.Count -gt 0) {
        $match = [regex]::Match($lines[0], '\[gd_resource[^\]]*uid="(' + $UidPattern + ')"')
        if ($match.Success) {
            Add-OwnerEntry $match.Groups[1].Value $resourcePath $resourcePath 1
        }
    } elseif ($file.Extension -eq '.uid' -and $lines.Count -gt 0) {
        $match = [regex]::Match($lines[0], '^(' + $UidPattern + ')$')
        if ($match.Success) {
            $ownerPath = $resourcePath.Substring(0, $resourcePath.Length - 4)
            Add-OwnerEntry $match.Groups[1].Value $ownerPath $resourcePath 1
        }
    } elseif ($file.Extension -eq '.import') {
        for ($index = 0; $index -lt $lines.Count; $index++) {
            $match = [regex]::Match($lines[$index], '^uid="(' + $UidPattern + ')"')
            if ($match.Success) {
                $ownerPath = Resolve-ImportOwnerPath $lines $file.FullName
                Add-OwnerEntry $match.Groups[1].Value $ownerPath $resourcePath ($index + 1)
                break
            }
        }
    }
}

$OwnerEntries |
    Group-Object Uid |
    Where-Object { @($_.Group | Select-Object -ExpandProperty OwnerPath -Unique).Count -gt 1 } |
    ForEach-Object {
        Add-Failure "OWNER_UID_DUPLICATE uid=$($_.Name)"
        foreach ($entry in $_.Group) {
            Add-Failure "  owner=$($entry.OwnerPath) source=$($entry.SourcePath):$($entry.LineNumber)"
        }
    }

foreach ($sceneFile in Get-ProjectFiles @('.tscn', '.tres')) {
    $sceneResourcePath = Convert-ToResourcePath $sceneFile.FullName
    $lines = @(Get-Content -LiteralPath $sceneFile.FullName -Encoding UTF8)

    for ($index = 0; $index -lt $lines.Count; $index++) {
        $line = $lines[$index]
        if ($line -notmatch '^\[ext_resource ') {
            continue
        }

        $uidMatch = [regex]::Match($line, 'uid="(' + $UidPattern + ')"')
        $pathMatch = [regex]::Match($line, 'path="(res://[^"]+)"')
        if (-not $uidMatch.Success -or -not $pathMatch.Success) {
            continue
        }

        $actualUid = $uidMatch.Groups[1].Value
        $targetPath = $pathMatch.Groups[1].Value
        if (-not $OwnerUidByResourcePath.ContainsKey($targetPath)) {
            continue
        }

        $expectedUid = [string]$OwnerUidByResourcePath[$targetPath]
        if ($actualUid -ne $expectedUid) {
            Add-Failure (
                "EXT_RESOURCE_UID_MISMATCH scene={0}:{1} path={2} actual={3} expected={4}" -f
                    $sceneResourcePath,
                    ($index + 1),
                    $targetPath,
                    $actualUid,
                    $expectedUid
            )
        }
    }
}

if ($Failures.Count -gt 0) {
    $Failures | ForEach-Object { Write-Error $_ -ErrorAction Continue }
    exit 1
}

Write-Host "Godot UID verification passed."
