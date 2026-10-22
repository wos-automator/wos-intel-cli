# Runs the spec-validator release pinned in VERSION on Windows (nice to have, see README).
# The binary is downloaded once into the user cache and verified against checksums.txt.
# $env:SPEC_VALIDATOR = <path> runs another binary.
$ErrorActionPreference = 'Stop'

if ($env:SPEC_VALIDATOR) {
    & $env:SPEC_VALIDATOR @args
    exit $LASTEXITCODE
}

$version = (Get-Content (Join-Path $PSScriptRoot 'VERSION') -Raw).Trim()
$arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'amd64' }
$cache = Join-Path $env:LOCALAPPDATA "spec-validator\$version"
$binary = Join-Path $cache 'spec-validator.exe'

if (-not (Test-Path $binary)) {
    $archive = "spec-validator_${version}_windows_$arch.zip"
    $url = "https://github.com/thst71/spec-validator/releases/download/v$version/$archive"
    $line = Get-Content (Join-Path $PSScriptRoot 'checksums.txt') | Where-Object { ($_ -split '\s+')[1] -eq $archive }
    if (-not $line) { Write-Error "validate-specs: no checksum for $archive"; exit 2 }
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
