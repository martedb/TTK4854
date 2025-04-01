import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from folium.plugins import HeatMap

# === File paths ===
ghost_nets_csv = "/var/www/html/mywebsite/ghost_nets.csv"
protected_geojson = "/var/www/html/mywebsite/marine_protected_areas_4326.geojson"
spawning_geojson = "/var/www/html/mywebsite/spawning_areas.geojson"
output_file = "/var/www/html/mywebsite/norway_ghost_nets_map.html"

# === Load ghost nets ===
data = pd.read_csv(ghost_nets_csv)
data = data.dropna(subset=['latitude', 'longitude', 'weight'])

gdf_nets = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data.longitude, data.latitude),
    crs="EPSG:4326"
)

# === Load protected areas and reproject ===
gdf_protected = gpd.read_file(protected_geojson)
gdf_protected = gdf_protected.to_crs(gdf_nets.crs)

# === Load spawning areas and reproject ===
gdf_spawning = gpd.read_file(spawning_geojson)
gdf_spawning = gdf_spawning.to_crs(gdf_nets.crs)

# === Check which ghost nets are in protected areas ===
gdf_nets['in_protected_area'] = False
joined_protected = gpd.sjoin(gdf_nets, gdf_protected, how='left', predicate='within')
gdf_nets.loc[joined_protected.index, 'in_protected_area'] = joined_protected['index_right'].notna()

# === Check which ghost nets are in spawning areas ===
gdf_nets['in_spawning_area'] = False
joined_spawning = gpd.sjoin(gdf_nets, gdf_spawning, how='left', predicate='within')
gdf_nets.loc[joined_spawning.index, 'in_spawning_area'] = joined_spawning['index_right'].notna()

# === Scale ghost net radius based on weight ===
def scaled_radius(weight, base=50, scale=30, max_radius=400):
    return min(base + scale * (weight ** 0.5), max_radius)

gdf_nets['radius_m'] = gdf_nets['weight'].apply(scaled_radius)

# === Convert Timestamp columns to strings for GeoJson serialization ===
gdf_protected = gdf_protected.copy()
gdf_spawning = gdf_spawning.copy()
gdf_protected = gdf_protected.applymap(lambda x: str(x) if isinstance(x, pd.Timestamp) else x)
gdf_spawning = gdf_spawning.applymap(lambda x: str(x) if isinstance(x, pd.Timestamp) else x)

# === Create map ===
m = folium.Map(location=[65, 13], zoom_start=5, tiles="OpenStreetMap")

# === Add ghost net circles with color based on area ===
for _, row in gdf_nets.iterrows():
    if row['in_protected_area']:
        color = 'red'
    elif row['in_spawning_area']:
        color = 'red'
    else:
        color = '#5A5A5A'  # dark grey

    folium.Circle(
        location=[row['latitude'], row['longitude']],
        radius=row['radius_m'],  # meters
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
                popup=(
            f"No. of nets in location: {row['weight']}<br>"
            f"In Protected Area: {row['in_protected_area']}<br>"
            f"In Spawning Area: {row['in_spawning_area']}"
        )
    ).add_to(m)

# === Add marine protected areas layer ===
folium.GeoJson(
    gdf_protected,
    name="Marine Protected Areas",
    style_function=lambda feature: {
        "fillColor": "blue",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.3,
    },
).add_to(m)

# === Add spawning areas layer ===
folium.GeoJson(
    gdf_spawning,
    name="Spawning Areas",
    style_function=lambda feature: {
        "fillColor": "orange",
               "color": "darkorange",
        "weight": 1,
        "fillOpacity": 0.3,
    },
).add_to(m)

# === Add toggleable heatmap ===
heat_data = gdf_nets[['latitude', 'longitude', 'weight']].values.tolist()
heatmap_layer = folium.FeatureGroup(name="Ghost Net Heatmap", show=False)
HeatMap(heat_data, radius=10, blur=10, max_zoom=1).add_to(heatmap_layer)
heatmap_layer.add_to(m)

# === Add layer control ===
folium.LayerControl(collapsed=False).add_to(m)

# === Save map ===
m.save(output_file)
print(f"Map saved to {output_file}")