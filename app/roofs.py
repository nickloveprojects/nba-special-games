"""Stadium roofs. ESPN has a single 'indoor' flag that is True for retractable roofs too, which would wrongly
treat a game as played indoors. Roof types here are checked against each stadium's own description.
  fixed        fully enclosed, always indoors
  retractable  roof can be open or closed; the home team decides close to kickoff, so we cannot know in advance
  canopy       fixed roof over the seats with open sides (SoFi): rain is kept off, wind still gets in
  open         no roof
Anything ESPN calls indoor that is not in this table is treated as retractable (unconfirmed), never as indoors."""
from __future__ import annotations

# keyword in the venue name (lowercase) -> roof type
ROOFS = {
    "ford field": "fixed",              # Detroit
    "superdome": "fixed",               # New Orleans
    "u.s. bank stadium": "fixed",       # Minnesota
    "us bank stadium": "fixed",
    "allegiant": "fixed",               # Las Vegas
    "state farm stadium": "retractable",  # Arizona
    "mercedes-benz stadium": "retractable",  # Atlanta
    "at&t stadium": "retractable",      # Dallas
    "nrg stadium": "retractable",       # Houston
    "reliant stadium": "retractable",
    "lucas oil": "retractable",         # Indianapolis
    "bernab": "retractable",            # Madrid (neutral-site game)
    "sofi stadium": "canopy",           # Los Angeles Rams and Chargers
}
SOURCE = ("Stadium roof types: team and stadium sites for ARI, ATL, DAL, HOU, IND (retractable), DET, NO, MIN, LV (fixed), "
          "SoFi (canopy). Checked 2026-11.")


def roof_for(arena: str, espn_indoor: bool) -> str:
    name = (arena or "").lower()
    for key, kind in ROOFS.items():
        if key in name:
            return kind
    return "retractable" if espn_indoor else "open"
