# Data Directory

This directory contains persistent data for the LangGraph RAG system.

## Structure

```
data/
├── qdrant_storage/          # Qdrant vector database files
│   ├── collections/         # Vector collections data
│   ├── snapshots/          # Collection snapshots
│   └── wal/                # Write-ahead log
├── uploads/                # Uploaded documents
│   ├── processed/          # Processed document chunks
│   └── metadata/           # Document metadata
└── models/                 # Cached model files
    ├── embeddings/         # Embedding model cache
    └── tokenizers/         # Tokenizer cache
```

## Important Notes

- **Qdrant Storage**: Contains all vector embeddings and document chunks
- **Backups**: Use `./scripts/manage_vectordb.sh backup` for data safety
- **Persistence**: Data persists between container restarts
- **Size**: Directory grows with uploaded documents and vector data

## Cleanup

To free up space:
```bash
# Remove processed uploads (safe)
rm -rf data/uploads/processed/*

# Reset all vector data (destructive)
./scripts/manage_vectordb.sh reset

# Clean model cache
rm -rf data/models/cache/*
```

## Backup Strategy

Regular backups are recommended:
```bash
# Create timestamped backup
./scripts/manage_vectordb.sh backup

# Restore from backup
./scripts/manage_vectordb.sh restore
```
