# Runs the spec-validator release pinned in the project's .agents/spec-validator.lock on Windows
# (nice to have, see README): an installed spec-validator of exactly that version, else the release
# binary, downloaded once into the user cache and verified against the lock.
# $env:SPEC_VALIDATOR = <path> runs another binary. To change the pin, run the sh launcher with
# --update (e.g. from Git Bash).
$ErrorActionPreference = 'Stop'

if ($args.Count -gt 0 -and $args[0] -eq '--update') {
    Write-Error 'validate-specs: --update needs the sh launcher: sh .agents/skills/spec-system/bin/validate-specs --update'
    exit 2
}

if ($env:SPEC_VALIDATOR) {
    & $env:SPEC_VALIDATOR @args
    exit $LASTEXITCODE
}

$lock = Join-Path $PSScriptRoot '..\..\..\spec-validator.lock'
if (-not (Test-Path $lock)) {
    Write-Error "validate-specs: no $lock; create it with: sh .agents/skills/spec-system/bin/validate-specs --update"
    exit 2
}
$lines = Get-Content $lock
$version = ($lines | Where-Object { ($_ -split '\s+')[0] -eq 'version' } | ForEach-Object { ($_ -split '\s+')[1] }) | Select-Object -First 1
if (-not $version) { Write-Error "validate-specs: no version line in $lock"; exit 2 }

$installed = Get-Command spec-validator -ErrorAction SilentlyContinue
if ($installed) {
    $installedVersion = (& $installed.Source -version 2>$null | Out-String).Trim().TrimStart('v')
    if ($installedVersion -eq $version) {
        & $installed.Source @args
        exit $LASTEXITCODE
    }
}

$arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'amd64' }
$cache = Join-Path $env:LOCALAPPDATA "spec-validator\$version"
$binary = Join-Path $cache 'spec-validator.exe'

if (-not (Test-Path $binary)) {
    $archive = "spec-validator_${version}_windows_$arch.zip"
    $url = "https://github.com/thst71/spec-validator/releases/download/v$version/$archive"
    $line = $lines | Where-Object { ($_ -split '\s+')[1] -eq $archive }
    if (-not $line) { Write-Error "validate-specs: no checksum for $archive in $lock"; exit 2 }
    $expected = ($line -split '\s+')[0]

    $work = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid())
    New-Item -ItemType Directory -Path $work | Out-Null
    try {
        Invoke-WebRequest -Uri $url -OutFile (Join-Path $work $archive) -UseBasicParsing
        $actual = (Get-FileHash (Join-Path $work $archive) -Algorithm SHA256).Hash.ToLower()
        if ($actual -ne $expected) { Write-Error "validate-specs: checksum mismatch for $archive"; exit 2 }
        Expand-Archive (Join-Path $work $archive) -DestinationPath $work
        New-Item -ItemType Directory -Force -Path $cache | Out-Null
        Move-Item (Join-Path $work 'spec-validator.exe') $binary
    } finally {
        Remove-Item -Recurse -Force $work
    }
}

& $binary @args
exit $LASTEXITCODE
