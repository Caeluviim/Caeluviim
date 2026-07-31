$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Push-Location $Root

$Stopped = $false
try {
    if (-not (Test-Path ".env")) {
        throw "Missing .env. Run scripts/laptop/start.ps1 first."
    }

    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $HostBackup = Join-Path $Root "backups/$Stamp"
    New-Item -ItemType Directory -Path $HostBackup -Force | Out-Null

    docker compose stop neo4j
    if ($LASTEXITCODE -ne 0) { throw "Neo4j could not be stopped for the offline backup." }
    $Stopped = $true

    docker compose --profile admin run --rm neo4j-admin database dump neo4j --to-path="/backups/$Stamp" --overwrite-destination=true
    if ($LASTEXITCODE -ne 0) { throw "The neo4j database dump failed." }

    docker compose --profile admin run --rm neo4j-admin database dump system --to-path="/backups/$Stamp" --overwrite-destination=true
    if ($LASTEXITCODE -ne 0) { throw "The system database dump failed." }

    $Checksums = Get-ChildItem $HostBackup -Filter "*.dump" | Sort-Object Name | ForEach-Object {
        $Hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$Hash  $($_.Name)"
    }
    [System.IO.File]::WriteAllLines(
        (Join-Path $HostBackup "SHA256SUMS.txt"),
        $Checksums,
        (New-Object System.Text.UTF8Encoding($false))
    )

    Write-Host "Backup complete: $HostBackup"
}
finally {
    if ($Stopped) {
        docker compose up -d neo4j | Out-Host
    }
    Pop-Location
}
