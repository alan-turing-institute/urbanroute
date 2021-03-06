"""Short script used for loading a target graph using osmnx, updating the costs of the edges using up-to-date pollution data, and storing that graph in .gt format"""
from typing import Optional
import osmnx as ox
import logging
import geopandas as gpd
import os
import typer
import matplotlib.pyplot as plt
from urbanroute.geospatial import update_cost, ellipse_bounding_box
from urbanroute.queries import HexGridQuery
from graph_tool.all import *
from cleanair.loggers import get_logger

logger = get_logger("Loading graph")
logger.setLevel(logging.DEBUG)


def main(secretfile: str):
    logger.info("Loading air pollution results")
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
    gdf = gpd.GeoDataFrame.from_postgis(
        result_sql, result_query.dbcnxn.engine, crs=4326
    )
    # May need to switch to mercator projection to match Mapbox's projection - a different EPSG code than 4326
    gdf.crs = "EPSG:4326"
    gdf.to_crs(epsg="3857")
    gdf.plot(column="NO2_mean")
    plt.axis("off")
    plt.savefig(
        "pollution.png",
        transparent=True,
        dpi=1000,
        cmap="inferno",
        bbox_inches="tight",
        pad_inches=0,
    )
    logger.info(plt.ylim())
    logger.info(plt.xlim())
    plt.show()
    gdf.to_crs(epsg="4326")
    gdf = gdf.rename(columns=dict(geom="geometry"))
    logger.info(gdf.columns)
    # load target graph in osmnx
    G = update_cost(
        # ox.graph.graph_from_bbox(51.505243, 51.502915, -0.152267, -0.145845),
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


if __name__ == "__main__":
    typer.run(main)
