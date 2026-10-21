# Architecture

How NeoArch is put together. The codebase is split into a **backend** that
never imports GUI code and a **frontend** that renders it — which is what lets
the same engine back both the desktop app and the headless `neo` CLI.

```
neoarch/
├── backend/          # headless core: no PyQt imports
│   ├── package/      # loaders, installer, updater, uninstaller
│   ├── services/     # feature services (aur, search, keyring, updates, …)
│   ├── auth.py, config_utils.py, sys_utils.py, workers.py
├── frontend/         # PyQt6 UI
│   ├── components/   # reusable widgets (cards, tables, dialogs)
│   ├── dialogs/      # modal dialogs
│   ├── views/        # per-tab views
│   ├── mixins/       # behaviour mixed into views
│   └── main_window.py
├── managers/         # plugin manager
├── cli.py            # `neo` command line interface
├── locale/           # 10 shipped translations
└── resources/        # version, paths, assets
```

## Backend

| Area | Responsibility |
|---|---|
| `backend/package/loader.py` | Discovers installed packages per source (pacman, AUR, flatpak, npm, pipx) and parses their state |
| `backend/package/installer.py` | Runs installs/removals, privilege escalation, and transaction logging |
| `backend/package/updater.py` | Detects available updates and applies them |
| `backend/services/` | One module per feature: AUR search and builds, repo management, keyring, snapshots, hygiene, release notes, scheduler |
| `backend/workers.py` | Thread offloading so the UI never blocks on subprocesses |
| `backend/services/i18n.py` | Translation loading and lookup |

Package sources are implemented behind a common interface: each loader reports
packages in a normalised shape, so the UI and the CLI treat pacman, AUR,
Flatpak, npm, and pipx uniformly.

## Frontend

The main window is composed of tabs (Discover, Installed, Updates, Plugins,
Settings, …). Views live in `frontend/views/`, reusable widgets in
`frontend/components/`, and shared behaviour in `frontend/mixins/`. Long
operations are handed to `backend/workers.py` and report back through signals.

## CLI

`neoarch/cli.py` exposes the same backend over a terminal with `--json` output
for scripting, so the GUI is a client of the engine rather than its owner.

## Packaging

- `packaging/` holds the PKGBUILDs, the AppStream metadata, and the desktop file.
- `.github/workflows/` publishes the `neoarch` (stable) and `neoarch-git`
  (development) packages to the AUR.
- The AppStream ID and desktop `Icon=` key are stable identifiers and are
  intentionally **not** renamed when the project moves hosts.

## See also

- [Development Setup](Development-Setup.md)
- [Contributing](Contributing.md)
- [Plugin Development](Plugin-Development.md)
