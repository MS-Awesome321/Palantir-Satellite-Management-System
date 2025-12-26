from poliastro.czml.extract_czml import CZMLExtractor # type: ignore
from poliastro.examples import molniya, iss # type: ignore
from poliastro.twobody import Orbit # type: ignore
from poliastro.bodies import Earth # type: ignore
from astropy import units as u
from helpers import write_packets

start_epoch = iss.epoch
print(start_epoch)
end_epoch = iss.epoch + molniya.period
print(end_epoch)
sample_points = 100

extractor = CZMLExtractor(start_epoch, end_epoch, sample_points)

extractor.add_orbit(
    molniya,
    id_name="Molniya_Orbit",
    path_width=2,
    label_text="Molniya",
    path_color=[125, 80, 120, 255],
)

extractor.add_orbit(
    iss,
    id_name="ISS_Orbit",
    path_width=2,
    label_text="ISS",
    path_color=[0, 255, 255, 255]
)

test_orbit = Orbit.from_classical(
    Earth, # Center
    a = 25000 << u.kilometer, # Semi-Major Axis (km)
    ecc = .5 << u.one, # Eccentricity
    inc= 45 << u.deg, # Inclination (deg)
    raan=90 << u.deg, # Right Ascension of the Ascending Node (deg)
    argp=0 << u.deg, # Argument of Periapsis (deg)
    nu=0 << u.deg # True Anomaly (Phase Shift) (deg)
)

extractor.add_orbit(
    test_orbit,
    id_name="Test_Orbit",
    path_width=2,
    label_text="Test",
    path_color=[0, 255, 0, 255]
)

write_packets(extractor.packets, "static/czml/test.czml")