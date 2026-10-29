"""Trade confirmation. Trades come from ESPN's transactions feed (recent months) and from an optional CSV you
maintain for older ones: date,player,from_team,to_team,type  (teams = abbreviation)."""
import csv
import logging
from pathlib import Path

from ..rules import norm_name
from ..teams_geo import team_id

log = logging.getLogger("nba")


def save_trades(conn, trades: list[dict], source: str) -> int:
    n = 0
    for t in trades:
        cur = conn.execute("INSERT OR IGNORE INTO transactions(date,player_name,from_team_id,to_team_id,type,source) "
                           "VALUES(?,?,?,?,?,?)",
                           (t["date"], t["player_name"], t["from_team_id"], t["to_team_id"], t.get("type", "trade"), source))
        n += cur.rowcount
    conn.commit()
    return n


def import_csv(conn, path) -> int:
    path = Path(path)
    trades = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("player") or (r.get("type") or "trade").lower() != "trade":
                continue
            trades.append({"date": r["date"], "player_name": norm_name(r["player"]),
                           "from_team_id": team_id(r.get("from_team")), "to_team_id": team_id(r.get("to_team"))})
    return save_trades(conn, trades, path.name)


def confirmed_exit(conn, player_name: str, from_team: int) -> dict | None:
    """Latest recorded trade or waiver in which this player left `from_team`."""
    r = conn.execute("SELECT * FROM transactions WHERE player_name=? AND from_team_id=? AND type IN ('trade','waive') "
                     "ORDER BY date DESC LIMIT 1", (norm_name(player_name), from_team)).fetchone()
    return dict(r) if r else None
