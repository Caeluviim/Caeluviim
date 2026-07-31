param(
    [Parameter(Mandatory = $true)]
    [string]$BackupName
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Push-Location $Root

$Stopped = $false
try {
    $BackupRoot = (Resolve-Path (Join-Path $Root "backups")).Path
    $Selected = (Resolve-Path (Join-Path $BackupRoot $BackupName)).Path
    if (-not $Selected.StartsWith($BackupRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Backup must be a directory beneath $BackupRoot."
    }

    foreach ($Name in @("neo4j.dump", "system.dump")) {
        if (-not (Test-Path (Join-Path $Selected $Name))) {
            throw "Backup is incomplete: missing $Name."
        }
    }

    $ChecksumFile = Join-Path $Selected "SHA256SUMS.txt"
    if (Test-Path $ChecksumFile) {
        foreach ($Line in Get-Content $ChecksumFile) {
            if ($Line -match '^([0-9a-fA-F]{64})\s+\*?(.+)$') {
                $Expected = $Matches[1].ToLowerInvariant()
                $FileName = $Matches[2].Trim()
                $Actual = (Get-FileHash (Join-Path $Selected $FileName) -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($Actual -ne $Expected) {
                    throw "Checksum verification failed for $FileName."
                }
            }
        }
    }

    docker compose stop neo4j
    if ($LASTEXITCODE -ne 0) { throw "Neo4j could not be stopped for restore." }
    $Stopped = $true

    docker compose --profile admin run --rm neo4j-admin database load --from-path="/backups/$BackupName" neo4j --overwrite-destination=true
    if ($LASTEXITCODE -ne 0) { throw "The neo4j database restore failed." }

    docker compose --profile admin run --rm neo4j-admin database load --from-path="/backups/$BackupName" system --overwrite-destination=true
    if ($LASTEXITCODE -ne 0) { throw "The system database restore failed." }

    Write-Host "Restore complete from $Selected"
}
finally {
    if ($Stopped) {
        docker compose up -d neo4j | Out-Host
    }
    Pop-Location
}
