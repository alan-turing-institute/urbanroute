"""Short script used for loading a target graph using osmnx, updating the costs of the edges using up-to-date pollution data, and storing that graph in .gt format"""
from typing import Optional
import osmnx as ox
import geopandas as gpd
import os
from urbanroute.geospatial import update_cost, ellipse_bounding_box
from urbanroute.queries import HexGridQuery
from graph_tool.all import *

print("Loading air pollution results")
secretfile: str = "/home/james/clean-air-infrastructure/.secrets/db_secrets_ad.json"
instance_id: str = "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737"
start_time: Optional[str] = "2020-01-24T09:00:00"
upto_time: Optional[str] = "2020-01-24T10:00:00"
result_query = HexGridQuery(secretfile=secretfile)
result_sql = result_query.query_results(
    instance_id,
    join_hexgrid=True,
    output_type="sql",
    start_time=start_time,
    upto_time=upto_time,
)
gdf = gpd.GeoDataFrame.from_postgis(result_sql, result_query.dbcnxn.engine, crs=4326)
gdf = gdf.rename(columns=dict(geom="geometry"))
gdf.crs = "EPSG:4326"

# load target graph in osmnx
G = update_cost(
    ox.graph.graph_from_address("Trafalgar Square, Charing Cross, London WC2N 5DN"),
    gdf,
    cost_attr="NO2_mean",
    weight_attr="length",
)

# save target graph as a .gt file
ox.io.save_graphml(G, "./Trafalgar.graphml")
G = graph_tool.load_graph("./Trafalgar.graphml")
os.remove("./Trafalgar.graphml")
G.save("./Trafalgar.gt")
