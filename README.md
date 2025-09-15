# EPG Proxy with Guide Art Injection

This container ingests one or more XMLTV feeds, copies the `<icon src>` URL
into a new `tvc-guide-art` attribute on each `<channel>`, and republishes
the processed XML(s) at a simple web endpoint.

## Features
- Multiple feeds from a JSON config
- Friendly names (auto-slugified into URLs)
- Index page at `/epg/` with last refresh time
- Auto-refresh every N hours (default 12, configurable with `REFRESH_HOURS`)

## Example Config
In Portainer stack:

```yaml
configs:
  epg_config:
    data: |
      {
        "feeds": [
          {
            "name": "Dispatcharr",
            "url": "http://192.168.0.37:9191/api/epg/Dispatcharr.xml"
          },
          {
            "name": "Pluto TV",
            "url": "http://192.168.0.37:9191/api/epg/Pluto.xml"
          }
        ]
      }
```

## Endpoints
- Index: `http://<host>:5000/epg/`
- Feed:  `http://<host>:5000/epg/dispatcharr.xml`
- Feed:  `http://<host>:5000/epg/pluto-tv.xml`
