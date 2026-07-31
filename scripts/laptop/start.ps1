$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Push-Location $Root

try {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker Desktop is not installed or docker is not on PATH."
    }

    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Desktop is not running. Start it and run this command again."
    }

    $EnvPath = Join-Path $Root ".env"
    if (-not (Test-Path $EnvPath)) {
        $Bytes = New-Object byte[] 24
        [System.Security.Cryptography.RandomNumberGenerator]::Fill($Bytes)
        $Password = [Convert]::ToHexString($Bytes).ToLowerInvariant()
        $Content = @"
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=$Password
NEO4J_DATABASE=neo4j
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
NEO4J_HEAP_INITIAL=512m
NEO4J_HEAP_MAX=1G
NEO4J_PAGECACHE=512m
"@
        [System.IO.File]::WriteAllText(
            $EnvPath,
            $Content,
            (New-Object System.Text.UTF8Encoding($false))
        )
        Write-Host "Created .env with a generated local Neo4j password."
    }

    $EnvText = Get-Content $EnvPath -Raw
    if ($EnvText -match "NEO4J_PASSWORD=replace-with-a-strong-local-password") {
        throw "Replace the placeholder NEO4J_PASSWORD in .env before starting the graph."
    }

    New-Item -ItemType Directory -Path (Join-Path $Root "backups") -Force | Out-Null

    docker compose config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose configuration validation failed." }

    docker compose up -d neo4j
    if ($LASTEXITCODE -ne 0) { throw "Neo4j failed to start." }

    docker compose build operator
    if ($LASTEXITCODE -ne 0) { throw "The graph operator image failed to build." }

    docker compose --profile operator run --rm operator sync
    if ($LASTEXITCODE -ne 0) { throw "Graph migration or corpus synchronization failed." }

    Write-Host ""
    Write-Host "Caeluviim graph host is operational."
    Write-Host "Neo4j Browser: http://localhost:7474"
    Write-Host "Bolt endpoint: neo4j://localhost:7687"
    Write-Host "Credentials are stored only in .env on this laptop."
}
finally {
    Pop-Location
}
