# Linux Quick Guide

## Authentication

The default `nlm login` opens your default browser (Firefox, Chrome, etc.) and extracts auth from a pasted cookie header. No browser launching required.

```bash
nlm login
```

### Steps

1. Log in to NotebookLM in the browser that opens
2. Press **F12** → **Network** tab → refresh the page
3. Click any `batchexecute` request
4. In the right panel, go to **Headers** → **Request Headers**
5. Find the `Cookie:` line, copy the entire value
6. Paste it into the terminal when prompted

### Alternative: Chrome CDP mode

If you prefer the old automatic flow (launches a managed Chromium instance):

```bash
nlm login --chrome
```

### Manual file mode

```bash
nlm login --manual --file /path/to/cookies.txt
```

## Installation

```bash
uv tool install notebooklm-mcp-cli
```

After code changes (when developing locally):

```bash
uv cache clean && uv tool install --force .
```
