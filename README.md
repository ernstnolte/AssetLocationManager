# 🌲 Fleet Telemetry & Asset Tracker

A Django application built for monitoring deployed machinery, logging GPS telemetry pings via an Agent application, and displaying real-time asset routes on interactive satellite maps.

---

## Features

* **Asset Registry:** Manage machine entries, serial numbers, and total ping counts.
* **Telemetry Logs:** Tabular history of timestamps, latitudes, and longitudes per asset.
* **Layered Map:** Leaflet.js map (Esri World Imagery + Labels) with automated route polyline breadcrumbs.
* **Responsive Control Panel:** Dark-themed UI tailored for desktop and field visibility.

---

## Prerequisites & Tech Stack

* **Backend:** Python `3.11.x` or `3.12.x` / Django `4.2+`
* **Frontend:** Leaflet.js, HTML5, CSS3
* **Database:** SQLite (Default for development)

> **Note:** Python 3.14+ is not supported due to framework context-cloning compatibility issues. Stick to Python 3.11 or 3.12.
