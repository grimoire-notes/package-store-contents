# Grimoire Package Store

The content repository for **Package Store**, Grimoire's built-in catalog for apps and
widgets. This repository is data only: Grimoire fetches `index.json`, displays its
screenshots and metadata, and installs the package from the manifest each entry names.

## Layout

```text
index.json                         the catalog
schema/store.schema.json           the catalog's JSON Schema
packages/<package-id>/
  package.yaml                     the installable package manifest
  <artifact>                       the package's actual contents (normally a .wasm)
  icon.ico                         optional app icon
  screens/01-name.png              screenshots, in display order
```

All paths in `index.json` are relative to the file itself, so the catalog works
unchanged from `raw.githubusercontent.com`, a branch, or a local mirror. Absolute
`https://` asset URLs are also accepted.

## Publishing a package

### Too publish your Package
Open a Pull Request with your Package Added, We will run tests and verification if it passes. It will be added.

### Too update your Package
We will verify you are the developer of the Package, you must link too a repo you own (Including repo's from organizations) and we will verify and update your package
Open a PR with the updated package, We will run tests and verification if it passes. It will be added.

## Too remove your Package
We will verify you are the developer of the Package, you must link too a repo you own (Including repo's from organizations) and we will verify and update your package
Open a PR with the package removed, We will run tests and verification if it passes. It will be added.

1. Put the complete package in `packages/<id>/`: its `package.yaml`, artifact, optional
   `.ico` and one or more screenshots.
2. Add an entry to the `packages` array in `index.json`.
3. Keep the entry's `id`, `name`, `version`, `type` and `author` in step with the
   manifest. Package Store checks the manifest's id against the entry before installing.
4. Run `python3 tools/check.py` from this repository to validate the catalog, the
   relative paths, each manifest and every SHA-256 and size.
5. Commit and PR.

Screenshots should show the app or widget in use, not a title card. Use grayscale or
low-colour images at 1200–1800 px wide; Grimoire converts them to e-ink gray.

## `index.json`

```json
{
  "version": 1,
  "name": "Grimoire Package Store",
  "tagline": "Apps and widgets made for Grimoire.",
  "updated": "2026-11-22",
  "featured": "com.example.app",
  "packages": [
    {
      "id": "com.example.app",
      "name": "Example",
      "version": "1.0.0",
      "type": "app",
      "author": "Jane Doe",
      "category": "Writing",
      "summary": "One line for the card.",
      "description": "The full description shown on the package page.",
      "license": "MIT",
      "repository": "https://github.com/jane/example",
      "manifest": "packages/com.example.app/package.yaml",
      "icon": "packages/com.example.app/icon.ico",
      "screenshots": ["packages/com.example.app/screens/01-example.png"],
      "tags": ["writing", "example"],
      "added": "2026-11-22"
    }
  ]
}
```

`type` is `app` or `widget`. `icon` may be a bundled image path (`.ico`, `.png`,
`.jpg` or `.jpeg`) or one of Grimoire's built-in icon names, such as `package`,
`timer` or `calculator`.

The catalog is cached on the device at `grimoire/package-store/index.json`, and the
catalog's images at `grimoire/package-store/assets/`. If the network is unavailable,
Package Store keeps showing the last catalog it downloaded.

## Privacy and trust

Package Store does not run or review package code. Installing shows the package's
author, version and license-like details from its manifest, then asks for the same
trust confirmation as **Settings → Packages**. The manifest and artifact are checked
against the digests in `package.yaml` before anything is written.
