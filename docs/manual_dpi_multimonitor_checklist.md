# Manual Checklist - Multi-Monitor and DPI

Last updated: 2026-02-19

## 1) Goal

Reduce visual regressions in QML layouts (cut text, overlap, out-of-viewport items)
under real multi-monitor and mixed-scaling scenarios.

## 2) Minimum setup

- OS: Windows 10/11.
- Display A: laptop screen (for example 125% scaling).
- Display B: external monitor/TV (for example 100% scaling).
- App in current build (`dist/AiringDeck.exe`) and Python run (`python src/main.py`).

## 3) Required test matrix

- Resolutions:
  - 1920x1080
  - 2560x1440 (if available)
- Scaling:
  - 100%
  - 125%
  - 150%
- Modes:
  - normal window
  - maximized
  - fullscreen (when applicable)
- Placement:
  - startup on primary monitor
  - drag and full use on secondary monitor

## 4) UI checklist

### Header + filters

- Search field does not overlap controls on the right.
- Genre/sort combos show readable non-truncated text.
- `ASC/DESC` and `Reset` buttons are always visible.
- `Only today` checkbox remains readable on all scaling levels.

### Calendar and cards

- Long card titles wrap to multiple lines without horizontal clipping.
- Episode badge (`Ep.`) always stays inside the card.
- No overlap between cards in `Flow` while resizing.

### Details sidebar

- Main cover is always visible (or textual fallback appears).
- Long anime title must not clip against the right edge.
- `Progress/Next` fields stay aligned and readable.

### Dialogs and settings

- About and Settings dialogs are centered and fully visible.
- Close controls are keyboard accessible (`Tab`, `Enter`).
- Language switch does not break layout (IT/EN).

## 5) Keyboard accessibility checklist

- Continuous tab order:
  - search -> sync -> profile/login -> filters -> sort -> reset.
- `Enter`/`Space` work on:
  - sync
  - login/profile
  - selectable anime cards
- Focus indicator is visible on interactive elements.

## 6) Acceptance criteria

- No critical text clipping.
- No essential control unreachable.
- No blocking overlap in header/filters/sidebar.
- No crash/freeze during resize, monitor switch, or scaling switch.

## 7) Evidence to attach

- Screenshots:
  - `resources/images/qa/dpi_100_main.png`
  - `resources/images/qa/dpi_125_main.png`
  - `resources/images/qa/dpi_150_secondary.png`
- Short note for each anomaly with:
  - monitor/scaling
  - UI section
  - observed behavior
