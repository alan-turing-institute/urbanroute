"""Find the least cost path from source to target by minimising air pollution."""

import typer
from cleanair.databases.queries import AirQualityResultQuery
from cleanair.loggers import get_logger
import routex as rx
import urbanroute as ur

def main(instance_id: str, secretfile: str):
    """
    instance_id: Id of the air quality trained model.

    secretfile: Path to the database secretfile.
    """
    logger = get_logger("Shortest path entrypoint")
    result_query = AirQualityResultQuery(secretfile=secretfile)
    logger.info("Querying results from an air quality model")
    result_df = result_query.query_results(instance_id, join_metapoint=True, output_type="df")
    print(result_df.head())


if __name__ == "__main__":
    typer.run(main)
