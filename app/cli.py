import argparse
import logging
from datetime import date
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(prog="python -m app.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="build the slate (today ET, or next game day)")
    r.add_argument("--date", help="YYYY-MM-DD")
    r.add_argument("--preseason", action="store_true")
    r.add_argument("--days", type=int, default=1, help="how many game days to build (2 = today and the next game day)")
    r.add_argument("--notify", action="store_true")
    t = sub.add_parser("import-transactions", help="load trades from CSV (date,player,from_team,to_team,type)")
    t.add_argument("path")
    d = sub.add_parser("daemon", help="run the pipeline every morning (APScheduler)")
    d.add_argument("--hour", type=int, default=8)
    s = sub.add_parser("serve", help="dashboard + API")
    s.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if a.cmd == "run":
        from datetime import timedelta

        from . import output, pipeline
        target, built = (date.fromisoformat(a.date) if a.date else None), []
        for i in range(max(1, a.days)):
            slate = pipeline.run(target, a.preseason, a.notify and i == 0)
            print(f"{slate['date']}: {len(slate['entries'])} flagged players, {len(slate['warnings'])} warnings")
            built.append(slate["date"])
            target = date.fromisoformat(slate["date"]) + timedelta(days=1)
        if a.days > 1:   # the site only keeps today and the next game day
            output.finalize(built)
    elif a.cmd == "import-transactions":
        from . import db
        from .sources import transactions
        print(transactions.import_csv(db.connect(), Path(a.path)), "rows imported")
    elif a.cmd == "daemon":
        from apscheduler.schedulers.blocking import BlockingScheduler
        from . import config, pipeline
        sch = BlockingScheduler(timezone=config.TZ)
        sch.add_job(lambda: pipeline.run(notify=True), "cron", hour=a.hour, minute=0, misfire_grace_time=3600)
        logging.info("Scheduled daily at %02d:00 %s", a.hour, config.TZ)
        pipeline.run(notify=False)  # populate immediately on start
        sch.start()
    elif a.cmd == "serve":
        import uvicorn
        uvicorn.run("app.server:app", host="0.0.0.0", port=a.port)


if __name__ == "__main__":
    main()
