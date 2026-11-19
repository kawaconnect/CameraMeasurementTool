# Camera Wire Tool

A desktop tool (Python, Tkinter) for planning security-camera and low-voltage
installs on a floor plan. Load a draw.io floor plan, place devices, draw the
cable routes, set the real-world scale, and get cable lengths per device plus
a project bill of materials.

It started as a one-off for a single building addition and works on any
draw.io plan.

## Features

- Reads a `.drawio` floor plan: devices, legend and the embedded background
  image. DXF and SVG drawings can be imported when the optional importers
  are installed (source installs only, see Install).
- Drag devices, draw multi-point wire routes, calibrate the scale from a
  known dimension. Shift snaps a route to 0/45/90 degrees; the cursor snaps
  to device centers and wire ends.
- Cable types and BOM: per-symbol cable assignment (Cat6, Cat5e, RG59,
  fiber, speaker, alarm; the catalog is editable), running cost with waste
  and tax.
- Camera field of view: lens, sensor, resolution and mount height give
  IEC EN 62676-4 Detection / Observation / Recognition / Identification
  zones drawn on the map.
- Several floors in one project, aligned with two reference points per
  floor; risers between floors are counted.
- Map annotations, door numbers / tags on devices, and a per-floor print
  area.
- Exports: BOM CSV, a three-file CSV set (BOM, devices, wires), a PDF
  report, a readable layout PDF (one page per floor plus a key), and a PNG
  map snapshot.
- Undo/redo for every edit, autosave with crash recovery, atomic file
  writes, and a revision history inside the project file.

## Requirements

- Release builds: Windows 10/11 x64, or x86_64 Linux with glibc 2.35 or
  newer (Ubuntu 22.04+, Debian 12+, Fedora 36+). Nothing else to install.
- From source: Python 3.10 or newer with Tk 8.6 (`python3-tk` on
  Debian/Ubuntu; included with the python.org installers).

## Install

**Release build.** Download a file from the project's releases (table under
Downloads / Building) and run it.

**From source.**

```
pip install -r requirements.txt
python camera_wire_tool.py
```

This installs Pillow, sv-ttk, reportlab (PDF export) and defusedxml (safe
parsing of drawings from other people). `pip install .` also works and adds
a `camera-wire-tool` command. The DXF/SVG importers are optional extras:
`pip install ".[cad]"` (ezdxf, matplotlib, PyMuPDF). The release builds do
not include them; there the app says so and explains how to convert the
drawing.

## Usage

```
python camera_wire_tool.py [FILE]
python camera_wire_tool.py --version
python camera_wire_tool.py --help
```

`FILE` is a project (`.zsmt` or `.wiremap.json`) or a drawing (`.drawio`,
or `.dxf` / `.svg` with the importers). Without `FILE`, the app looks next
to the program and in a `data/` folder beside it: if there is exactly one
project or drawing it opens, otherwise the start screen lists recent and
nearby projects.

Typical flow:

1. Open the `.drawio` plan (File > Open, Ctrl+O).
2. Tools > Set Scale (calibrate): click two points of a known dimension and
   type its length. Lengths and the BOM are wrong until this is done, and
   the app warns you.
3. Move Mode: place and drag devices. Wire Mode: click a device, click
   along the route, right-click to finish.
4. Check the BOM tab (waste, tax, currency), then File > Export.
5. Save (Ctrl+S).

**Project files.** Saving writes the drawing (`.drawio`: device moves and
the legend, still editable in draw.io) and a `.wiremap.json` project file
beside it (wire routes, scale, cable types, floors). Each save also adds a
revision to a `.zsmt` bundle in the same folder: one zip with the project,
every floor's drawing and the earlier saves (File > Revisions / revert).
The bundle is the file to hand to someone else; opening one unpacks it into
a `<name>_work` folder beside it.

Drawings saved with draw.io's "Compressed" option cannot be read: in
draw.io use File > Properties, untick Compressed, and save again.

For the simpler PNG-only measurement tool (kept for quick one-off
measurements) see `old/`.

### Controls

| Action | Control |
|--------|---------|
| Zoom | Mouse wheel (toward cursor), or Ctrl + scroll / pinch on a touchpad |
| Pan | Middle-click drag, Ctrl + left-drag, or two-finger scroll |
| Select / drag device | Left-click (Move Mode) |
| Place wire point | Left-click (Wire Mode) |
| Finish wire route | Right-click |
| Cancel current action | Escape, or right-click with fewer than 2 points |
| Delete selection | Delete |
| Undo / redo | Ctrl+Z / Ctrl+Y |
| Fit to view | Home |
| Save / Save As | Ctrl+S / Ctrl+Shift+S |
| Preferences | Ctrl+, |

Help > Keyboard Shortcuts lists the rest.

## Configuration

Settings are changed in the app (Tools > Preferences, the View menu, the
BOM tab) and kept per user in the home folder:

| File | Holds |
|------|-------|
| `~/.camera_wire_tool_settings.json` | Preferences, window placement, view options |
| `~/.camera_wire_tool_recent.json` | Recent files list |
| `~/.camera_wire_tool.log` | Error log (rotated to `.log.old` at about 512 KB) |

Delete the settings file to go back to defaults. Cable types, camera
models, scale and everything else about a job are stored in the project,
not in these files. There are no environment variables and no network
access: the app never downloads or uploads anything.

## Troubleshooting

- **Something failed and the message was not enough.** Help > Open log
  file shows `~/.camera_wire_tool.log` with the full error.
- **"This copy of Camera Wire Tool can't open DXF/SVG drawings."** The
  release builds leave the importers out. Export the plan as PNG, place it
  in draw.io and save as `.drawio`, or run from source with
  `pip install ".[cad]"`.
- **"This drawing was saved compressed by draw.io."** See Project files
  above.
- **"This file isn't a readable draw.io drawing."** The file is damaged,
  is not XML, or contains a DTD / entity declaration, which the app
  refuses on purpose.
- **Lengths look wrong.** The scale is not set or was set on the wrong
  dimension: run Tools > Set Scale again.
- **The app closed or crashed mid-edit.** Reopen the project: an autosave
  is written every minute next to the project (`*.autosave.json`) and the
  app offers to recover it.
- **No theme, plain grey widgets (source install).** `sv-ttk` is missing:
  `pip install -r requirements.txt`.
- **`ModuleNotFoundError: tkinter` (Linux source install).** Install your
  distribution's Tk package, for example `sudo apt install python3-tk`.
- **AppImage will not start on an older distro.** It needs glibc 2.35 or
  newer; RHEL/Rocky/Alma 9 have 2.34. Use the Flatpak there.
- **Flatpak cannot see a drive or network share.** It is sandboxed to the
  home folder. Copy the files there, or grant access with
  `flatpak override --user --filesystem=/path com.kawaconnect.CameraWireTool`.

## Security notes

Drawings and projects often come from someone else. `.drawio` files are
parsed with defusedxml and refused if they carry a DTD or entity
declaration. A `.zsmt` bundle is unpacked to flat file names only, so it
cannot write outside its `_work` folder. CSV exports prefix cells that a
spreadsheet would run as a formula (`=`, `+`, `-`, `@`) with an apostrophe.
The release builds are not code-signed, so Windows SmartScreen will warn on
first run.

## Downloads / Building

Release builds come from the GitLab pipeline (`.gitlab-ci.yml`) and appear
under **Deploy → Releases** of the GitLab project, with the files stored in
its **Package Registry** (generic package `CameraWireTool`, one version per
release):

| File | What it is |
|------|------------|
| `CameraWireTool-<ver>-windows-x64-setup.exe` | Windows installer (per-user by default, no admin; Start menu + optional desktop shortcut) |
| `CameraWireTool-<ver>-windows-x64-portable.zip` / `CameraWireTool.exe` | Portable Windows exe, no install; put it next to your floor plans and it opens them |
| `CameraWireTool-<ver>-linux-x86_64.AppImage` | Linux, any distro with glibc 2.35+ (Ubuntu 22.04+, Debian 12+, Fedora 36+; not RHEL/Rocky/Alma 9, which have glibc 2.34): `chmod +x` and run |
| `CameraWireTool-<ver>-linux-x86_64.flatpak` | Linux Flatpak bundle: `flatpak install --user <file>` (pulls the freedesktop 25.08 runtime from Flathub) |

**Cutting a release:** first set the version in `cwt/__init__.py`
(`__version__`) and `pyproject.toml` to `X.Y.Z` and commit. The pipeline
fails if the tag differs from `cwt.__version__` or the `pyproject.toml`
version, because the app shows that version in its About screen and reports. Then push a tag `vX.Y.Z` (for
example `git tag v1.3.0 && git push origin v1.3.0`). The pipeline runs the
tests, builds every file above (Windows natively on the Windows runner, Linux
in containers) and publishes the release for that tag. To rebuild or
re-publish an existing tag, run the pipeline from the web UI (**Build →
Pipelines → Run pipeline**) **on the tag `vX.Y.Z` as the ref** with the
variable `RELEASE_VERSION=vX.Y.Z`. The test stage refuses a run whose ref is
not that tag, and the release job refuses to publish if the tag points at a
different commit from the one the pipeline built. A web/API run without `RELEASE_VERSION`
only builds; download the files from the job artifacts (kept 30 days). The
pipeline does not run on ordinary pushes.

The existing GitHub Actions workflow (`.github/workflows/build-exe.yml`) is
unchanged and still builds `CameraWireTool.exe` on github.com.

**Building locally**

```
pip install -r requirements.txt -r packaging/requirements-build.txt
pyinstaller --noconfirm camera_wire_tool.spec     # dist/CameraWireTool(.exe)
python packaging/check_bundle.py dist/CameraWireTool.exe   # or dist/CameraWireTool on Linux
packaging/linux/build_appimage.sh 0.0.0-dev       # Linux: AppImage in packaging/linux/out/
```

The spec stops the build if sv-ttk or reportlab is missing, so a build can no
longer ship without the theme or PDF export. The AppImage script downloads a
pinned appimagetool and checks its SHA-256. The Windows installer is built
with Inno Setup from `installer/windows.iss`. Inno Setup's licence terms
changed with recent releases: check them before using the installer
commercially. The app icon comes from
`packaging/make_icon.py`.

## Repo layout

```
camera_wire_tool.py      main app (Tk UI, command stack, file handling)
camera_wire_tool.spec    PyInstaller build spec
cwt/                     logic modules without UI dependencies
  bom.py                 cable catalog, BOM rollup, BOM CSV
  bundle.py              .zsmt project bundle with revision history
  export.py              PDF report and CSV writers
  fov.py                 IEC 62676-4 DORI cone math
  import_cad.py          DXF / SVG floor-plan import (optional extras)
  layout_pdf.py          readable layout PDF (one page per floor + key)
  lenses.py              sensor, lens and install presets
  models.py              TypedDicts: Device, WireRoute, SymbolType
  multifloor.py          project file format and floor alignment
  raster_import.py       PNG/JPG floor-plan helpers (not wired into the UI yet)
tests/                   pytest suite
packaging/               AppImage script, Flatpak manifest, icons, bundle check
installer/windows.iss    Inno Setup script
ci/tools-windows.ps1     toolchain bootstrap for the Windows CI runner
old/                     the earlier PNG-only measurement tool
PLAYBOOK.md              design notes from the first version (partly outdated)
```

## Development

```
pip install -r requirements-dev.txt   # adds pytest, ruff, mypy
pytest
```

Tests that open windows need a display and skip without one (as in the
Linux CI job). To run them headless: `xvfb-run -a pytest`. A few use a
sample project in `data/`, which is not in the repo, and skip without it.
`ruff check .` and `mypy cwt/` are configured in `pyproject.toml` but are
not part of CI and do not pass cleanly yet.

## License

MIT, see `LICENSE`.
