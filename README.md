# Kampoversikt for Gjerpen IF håndball

Spilte og kommende kamper for barne- og ungdomslagene i Gjerpen Idrettsforening håndball
(handball.no klubbid 60697). Damelaget er ikke med.

- `build.py` henter lagene og kampene fra handball.no og lager `ut/index.html` og `ut/kamper.json`.
- `mal.html` er utseendet på siden. Kampdataene settes inn ved bygging.
- `.github/workflows/oppdater.yml` kjører skriptet hver time og publiserer resultatet på GitHub Pages.

Kjør lokalt: `python3 build.py ut` og åpne `ut/index.html`.
