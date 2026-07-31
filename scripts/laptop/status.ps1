$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Push-Location $Root
try {
    docker compose ps
    $State = docker inspect --format '{{.State.Status}}' caeluviim-neo4j 2>$null
    if ($LASTEXITCODE -ne 0 -or $State -ne "running") {
        throw "The Caeluviim Neo4j container is not running."
    }

    docker compose --profile operator run --rm --no-deps operator health
    if ($LASTEXITCODE -ne 0) { throw "Neo4j health verification failed." }

    docker compose --profile operator run --rm --no-deps operator stats
    if ($LASTEXITCODE -ne 0) { throw "Graph statistics query failed." }
}
finally {
    Pop-Location
}
