# Lexicon

A personal vocabulary and reading trainer for articulate academic, public, and everyday English.

## Features
- Daily 200–350 word reading passage
- Clickable vocabulary in context
- Register guidance for conversation, public writing, and academic writing
- Comprehension and word-choice exercises
- Writing rewrite practice
- Speaking prompt
- Spaced review queue
- Personal “Found in the wild” vocabulary capture
- Searchable vocabulary bank
- Local browser progress storage

## Run locally
Open `index.html` directly in a browser, or use a local server.

## Deploy on GitHub Pages
1. Create a GitHub repository, e.g. `lexicon`.
2. Upload `index.html` and `README.md` to the repository root.
3. In GitHub, go to Settings → Pages.
4. Under “Build and deployment,” choose “Deploy from a branch.”
5. Select `main` and `/ (root)`.
6. Save. GitHub will publish the site at your Pages URL.

## Architecture
Version 1 is intentionally static and serverless. It uses browser `localStorage` for progress and does not require a database or API key.

## Suggested next phase
- Expand core bank to 1,000+ curated entries in a separate JSON file
- Add rotating reading library
- Add dynamic daily content generation through a serverless function/API
- Add authentic source links and RSS/news ingestion without reproducing copyrighted article text
- Add import/export of learning progress
- Add optional account sync
