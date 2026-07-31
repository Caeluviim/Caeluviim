$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Push-Location $Root
try {
    docker compose stop neo4j
    if ($LASTEXITCODE -ne 0) { throw "Neo4j failed to stop cleanly." }
    Write-Host "Caeluviim Neo4j is stopped. Persistent volumes were preserved."
}
finally {
    Pop-Location
}
