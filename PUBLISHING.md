# Publish Steps (HACS + Manual ZIP)

This package is ready to publish from:
`/Users/coreybusuttil/dev/github/tap/home-assistant/tap-home-assistant-integration`

## 1) Create standalone GitHub repository

```bash
mkdir -p /Users/coreybusuttil/dev/github/tap-home-assistant-integration
rsync -av --delete \
  /Users/coreybusuttil/dev/github/tap/home-assistant/tap-home-assistant-integration/ \
  /Users/coreybusuttil/dev/github/tap-home-assistant-integration/
cd /Users/coreybusuttil/dev/github/tap-home-assistant-integration
git init
git add .
git commit -m "Initial release: Tap Home Assistant integration v0.1.0"
```

If using GitHub CLI:

```bash
gh repo create coreybusuttil/tap-home-assistant-integration --public --source=. --remote=origin --push
```

## 2) Tag and release

```bash
cd /Users/coreybusuttil/dev/github/tap-home-assistant-integration
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

Create the release in GitHub UI:
- Tag: `v0.1.0`
- Title: `v0.1.0`
- Body: paste `RELEASE_v0.1.0.md`
- Attach asset: `dist/tap-home-assistant-integration-v0.1.0.zip`

Or with GitHub CLI:

```bash
gh release create v0.1.0 \
  dist/tap-home-assistant-integration-v0.1.0.zip \
  --title "v0.1.0" \
  --notes-file RELEASE_v0.1.0.md
```

## 3) Add to HACS (once)

In Home Assistant:
1. HACS -> Integrations -> three dots -> Custom repositories.
2. Add repository URL:
   - `https://github.com/coreybusuttil/tap-home-assistant-integration`
3. Category: `Integration`.
4. Install `Tap`.
5. Restart Home Assistant.

## 4) Manual ZIP fallback

Users can download:
- `https://github.com/coreybusuttil/tap-home-assistant-integration/releases/latest`

Then extract `custom_components/tap` into their HA config folder.
