import httpx


def get_canton_from_coordinates(coord_x: float, coord_y: float):
    """
    Query geo.admin.ch to find the canton for coordinates in EPSG:2056.
    Returns the canton name (string) or None if not found.
    """
    url = "https://api3.geo.admin.ch/rest/services/ech/MapServer/identify"
    params = {
        "geometry": f"{coord_x},{coord_y}",
        "geometryType": "esriGeometryPoint",
        "sr": "2056",
        "layers": "all:ch.swisstopo.swissboundaries3d-kanton-flaeche.fill",
        "tolerance": "0",
        "lang": "en",
    }

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()
        print(payload)

    for result in payload.get("results", []):
        attrs = result.get("attributes", {}) or {}
        # Try common attribute names used for canton labels
        for key in (
            "name",
            "NAME",
            "name_de",
            "NAME_DE",
            "KANTON",
            "kanton",
            "KANTONSNAME",
            "KANTONSBEZ",
            "KNT_NAME",
            "label",
        ):
            val = attrs.get(key)
            print(val)
            if isinstance(val, str) and val.strip():
                return val.strip()
        # Fallback: return first non-empty string attribute
        for val in attrs.values():
            if isinstance(val, str) and val.strip():
                return val.strip()

    return None
