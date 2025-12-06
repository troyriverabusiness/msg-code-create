#!/bin/bash
echo "🗑️  Deleting old database..."
rm server/data/travel.db

echo "🚆 Ingesting GTFS Data..."
uv run scripts/ingest_gtfs.py

echo "♿ Ingesting NeTEx Data (Enrichment)..."
uv run scripts/ingest_netex.py

echo "✅ Data Reset Complete!"
