#!/usr/bin/env python3

# Wait until osbuild compose build is finished

import json
import subprocess
import time
import sys

def get_composer_status() -> dict:
    """Get composer status as a dictionary

    Returns dict with keys:
      - running: list of running compose jobs
      - finished: list of finished compose jobs
      - failed: list of failed compose jobs
    """
    def _parse_composer_status(status_json:str) -> dict:
        status = json.loads(status_json)
        running = []
        finished = []
        failed = []
        for entry in status:
            if entry["path"] == "/compose/queue":
                running = entry["body"]["run"]
            elif entry["path"] == "/compose/finished":
                finished = entry["body"]["finished"]
            elif entry["path"] == "/compose/failed":
                failed = entry["body"]["failed"]
        return {
            "running": running,
            "finished": finished,
            "failed": failed
        }

    cmd = "composer-cli compose status --json"
    response = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    status_json = response.stdout
    return _parse_composer_status(status_json)

def does_compose_exist(compose_id:str, status:dict) -> bool:
    """Check if compose with given id exists in the given status."""
    composes = status["running"] + status["finished"] + status["failed"]
    for compose in composes:
        if compose["id"] == compose_id:
            return True
    return False

def is_build_finished(compose_id:str, status:dict):
    """Check if build with given id is finished."""
    for compose in status["finished"]:
        if compose["id"] == compose_id:
            return True
    return False

def is_build_failed(compose_id:str, status:dict):
    """Check if build with given id is failed."""
    for compose in status["failed"]:
        if compose["id"] == compose_id:
            return True
    return False

def wait_until_build_is_finished(compose_id:str, timeout_seconds:int):
    """Wait until build with given id is finished."""
    start_time = time.time()
    while True:
        status = get_composer_status()
        if is_build_finished(compose_id, status):
            return
        if is_build_failed(compose_id, status):
            raise Exception(f"Build {compose_id} failed")
        if time.time() - start_time > timeout_seconds:
            raise Exception(f"Timeout waiting for build {compose_id} to finish")
        time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <compose_id> <timeout_seconds>")
        sys.exit(1)

    compose_id = sys.argv[1]
    timeout_seconds = int(sys.argv[2])

    status = get_composer_status()

    if not does_compose_exist(compose_id, status):
        raise Exception(f"Compose with id {compose_id} does not exist")

    if is_build_finished(compose_id, status):
        print(f"Build with id {compose_id} is already finished")
        sys.exit(0)

    wait_until_build_is_finished(compose_id, timeout_seconds)
    print(f"Build with id {compose_id} is finished")
