import logging
import coloredlogs
import json
import os

from database import Database

logger = logging.getLogger("Database Testing")
coloredlogs.install(level='INFO', logger=logger)

def test_scenario(scenario_id, scenario_path):
    with open(os.path.join(scenario_path, "graph_build.json"), "r") as fp:
        build = json.load(fp)
    with open(os.path.join(scenario_path, "img_extract.json"), "r") as fp:
        extract = json.load(fp)
    with open(os.path.join(scenario_path, "graph_edits.json"), "r") as fp:
        edits = json.load(fp)
    with open(os.path.join(scenario_path, "expected_status.json"), "r") as fp:
        expected_status = json.load(fp)
    
    # Get status (this is only an example, test your code as you please as long as it works)
    status = {}
    if len(build) > 0:
        # Build graph
        db = Database(build[0][0])
        if len(build) > 1:
            db.add_nodes(build[1:])

        # Add extract
        db.add_extract(extract)
        # Graph edits
        db.add_nodes(edits)
        # Update status
        status = db.get_extract_status()
    
    if status == expected_status:
        logger.info("Test scenario {} succeeded".format(scenario_id))
    else:
        logger.error("Test scenario {} failed, ".format(scenario_id))
        
        for image in status.keys():
            if expected_status[image] != status[image]:
                logger.info("For image {}, expected status: {} but got status: {}".format(image, expected_status[image], status[image]))

if __name__ == "__main__":
    scenarios = [os.path.join('test_scenarios', scenario) for scenario in os.listdir('test_scenarios')]
    scenarios.sort()

    for test_id, scenario in enumerate(scenarios):
        test_scenario(test_id + 1, scenario)