import json
import os
from hashlib import sha256

from deb_pkg_tools.repo import update_repository
from falconpy import api_complete as FalconSDK

REPO = "/var/mirror/crowdstrike"
CONF = "~/.crowdstrike.json"


def get_creds(file=CONF):
    with open(os.path.expanduser(file), "r") as f:
        return json.load(f)


def check_hash(file, match, dir=REPO):
    if not os.path.isfile(f"{dir}/{file}"):
        return None
    filehash = sha256()
    with open(f"{dir}/{file}", "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            filehash.update(block)
    return filehash.hexdigest() == match


def valid_filename(file):
    return file.startswith("falcon-sensor_") and file.endswith(".deb")


def download_new_packages(falcon, dir=REPO):
    packages = {
        p["name"]: p["sha256"]
        for p in falcon.command(
            "GetCombinedSensorInstallersByQuery", parameters={"filter": 'os:"Debian"'}
        )["body"]["resources"]
    }

    for name, sha256 in packages.items():
        if valid_filename(name) and not check_hash(name, sha256):
            with open(f"{dir}/{name}", "wb") as f:
                f.write(
                    falcon.command(
                        "DownloadSensorInstallerById", parameters={"id": sha256}
                    )
                )

    return packages.keys()


def remove_old_packages(packages, dir=REPO):
    for file in os.listdir(dir) - packages:
        if valid_filename(file):
            os.remove(f"{dir}/{file}")


def main():
    falcon = FalconSDK.APIHarness(creds=get_creds())
    remove_old_packages(download_new_packages(falcon))
    update_repository(REPO)
    falcon.deauthenticate()
