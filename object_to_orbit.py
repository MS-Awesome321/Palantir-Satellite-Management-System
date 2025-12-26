from poliastro.czml.extract_czml import CZMLExtractor # type: ignore
import os
from satellite_viewer_sdk import FoundryClient # type: ignore
from foundry_sdk_runtime.auth import UserTokenAuth
from helpers import *
from astropy import units as u
import numpy as np

auth = UserTokenAuth(hostname="https://msawesome.usw-17.palantirfoundry.com", token=os.environ["FOUNDRY_TOKEN"])

client = FoundryClient(auth=auth, hostname="https://msawesome.usw-17.palantirfoundry.com")
AllOrbitingObjects = client.ontology.objects.OrbitingObject

def make_orbits(object_ids):
    orbits = []
    names = []
    for object_id in object_ids:
        sat = AllOrbitingObjects.get(object_id)
        names.append(sat.object_name)
        new_orbit = foundry_to_poliastro(sat)
        orbits.append(new_orbit)

    max_period = max([orbit.period for orbit in orbits])
    epochs = [orbit.epoch for orbit in orbits]
    unix_epochs = [epoch.to_value('unix', 'long') for epoch in epochs]
    print(unix_epochs)
    extractor = CZMLExtractor(epochs[np.argmin(unix_epochs)], epochs[np.argmax(unix_epochs)] + max_period, 150)

    for i in range(len(object_ids)):
        color = np.random.rand(3)
        color = np.append(color, 1)
        extractor.add_orbit(
            orbits[i],
            id_name=object_ids[i],
            path_width=2,
            label_text=names[i],
            path_color=color,
        )

    write_packets(extractor.packets, "static/czml/orbits.czml")