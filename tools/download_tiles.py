"""
Descarga tiles de OpenStreetMap para el área de Maturín y los guarda localmente.
Ejecutar: python tools/download_tiles.py
Genera tiles en static/tiles/{z}/{x}/{y}.png para visualización 100% offline.
"""
import os
import math
import time
import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TILES_DIR = os.path.join(BASE_DIR, 'static', 'tiles')
USER_AGENT = 'EpsilonUDO-Educational/1.0'

LAT_CENTER = 9.7456
LNG_CENTER = -63.1832
RADIUS_KM = 12.0

MIN_ZOOM = 13
MAX_ZOOM = 16
TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'

session = requests.Session()
session.headers.update({'User-Agent': USER_AGENT})

def lat_lng_to_tile(lat, lng, zoom):
    """Convierte lat/lng a coordenadas de tile (x, y) según OSM slippy map."""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = int((lng + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x, y

def tile_to_lat_lng(x, y, zoom):
    """Convierte coordenadas de tile a lat/lng (esquina NW del tile)."""
    n = 2.0 ** zoom
    lng = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lng

def get_tile_range(lat_center, lng_center, radius_km, zoom):
    """Calcula el rango de tiles (x_min, x_max, y_min, y_max) que cubren un radio dado."""
    from geopy.distance import distance
    north = distance(kilometers=radius_km).destination((lat_center, lng_center), 0)
    south = distance(kilometers=radius_km).destination((lat_center, lng_center), 180)
    east = distance(kilometers=radius_km).destination((lat_center, lng_center), 90)
    west = distance(kilometers=radius_km).destination((lat_center, lng_center), 270)

    x_nw, y_nw = lat_lng_to_tile(north.latitude, west.longitude, zoom)
    x_se, y_se = lat_lng_to_tile(south.latitude, east.longitude, zoom)

    x_min, x_max = min(x_nw, x_se), max(x_nw, x_se)
    y_min, y_max = min(y_nw, y_se), max(y_nw, y_se)
    return x_min, x_max, y_min, y_max

def download_tile(z, x, y):
    """Descarga un tile y lo guarda localmente. Retorna True si fue exitoso."""
    tile_dir = os.path.join(TILES_DIR, str(z), str(x))
    os.makedirs(tile_dir, exist_ok=True)
    tile_path = os.path.join(tile_dir, f'{y}.png')

    if os.path.exists(tile_path):
        return True

    url = TILE_URL.format(z=z, x=x, y=y)
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            with open(tile_path, 'wb') as f:
                f.write(resp.content)
            return True
        elif resp.status_code == 404:
            return False
        else:
            print(f'  HTTP {resp.status_code} para z={z} x={x} y={y}')
            time.sleep(0.5)
            return False
    except Exception as e:
        print(f'  Error: {e}')
        return False

def main():
    print(f'Descargando tiles offline para Maturín (z={MIN_ZOOM}-{MAX_ZOOM})...')
    print(f'Tiles se guardarán en: {TILES_DIR}')
    print()

    total_tiles = 0
    downloaded = 0
    skipped = 0
    failed = 0

    for zoom in range(MIN_ZOOM, MAX_ZOOM + 1):
        x_min, x_max, y_min, y_max = get_tile_range(LAT_CENTER, LNG_CENTER, RADIUS_KM, zoom)
        n_tiles = (x_max - x_min + 1) * (y_max - y_min + 1)
        total_tiles += n_tiles

        print(f'Zoom {zoom}: tiles {x_min}-{x_max}, {y_min}-{y_max} ({n_tiles} tiles)')

        count = 0
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                if download_tile(zoom, x, y):
                    downloaded += 1
                else:
                    failed += 1
                count += 1
                if count % 10 == 0:
                    print(f'  Progreso z{zoom}: {count}/{n_tiles}')
            time.sleep(0.3)

        print(f'  Zoom {zoom} completo: {n_tiles} tiles')
        print()

    print(f'Total tiles esperados: {total_tiles}')
    print(f'Descargados: {downloaded}')
    print(f'Fallidos: {failed}')
    print('¡Descarga completa!')

if __name__ == '__main__':
    main()