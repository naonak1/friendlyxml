import json, requests, io, re, os
from datetime import datetime
from flask import Flask, send_file
from lxml import etree
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

with open("config.json") as f:
    CONFIG = json.load(f)

# {slug: {"friendly": str, "xml": bytes, "last_updated": str}}
CACHE = {}

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def process_feed(name, url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        xml = etree.fromstring(r.content)

        # Step 1: build channel_id → icon_url map
        channel_icons = {}
        for chan in xml.findall("channel"):
            icon = chan.find("icon")
            if icon is not None and "src" in icon.attrib:
                channel_icons[chan.attrib["id"]] = icon.attrib["src"]

        # Step 2: apply icons to each programme
        for prog in xml.findall("programme"):
            chan_id = prog.attrib.get("channel")
            if chan_id in channel_icons:
                prog.attrib["tvc-guide-art"] = channel_icons[chan_id]

        slug = slugify(name)
        CACHE[slug] = {
            "friendly": name,
            "xml": etree.tostring(xml, encoding="utf-8", xml_declaration=True),
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        }
        print(f"[INFO] Updated feed {name} with {len(channel_icons)} channel icons")
    except Exception as e:
        print(f"[ERROR] Updating {name}: {e}")

def refresh_all():
    for feed in CONFIG["feeds"]:
        process_feed(feed["name"], feed["url"])

@app.route("/epg/<slug>.xml")
def serve_feed(slug):
    if slug not in CACHE:
        return "Feed not found", 404
    return send_file(io.BytesIO(CACHE[slug]["xml"]), mimetype="application/xml")

@app.route("/epg/")
def list_feeds():
    links = []
    for slug, data in CACHE.items():
        links.append(
            f'<li><a href="/epg/{slug}.xml">{data["friendly"]}</a> '
            f'(last updated: {data["last_updated"]})</li>'
        )
    return f"<h1>Available Feeds</h1><ul>{''.join(links)}</ul>"

# schedule refresh (default 12h)
refresh_hours = int(os.getenv("REFRESH_HOURS", "12"))
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_all, "interval", hours=refresh_hours)
scheduler.start()

# initial pull
refresh_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
