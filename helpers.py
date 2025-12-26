import math
from scipy.optimize import newton
import numpy as np
from astropy import units as u
from poliastro.bodies import Earth # type: ignore
from poliastro.twobody import Orbit # type: ignore
from scipy.spatial.distance import cdist
from astropy.time import Time

def get_angle(cos, sin):
    '''Get angle from cos and sin (0 to 2pi)'''
    cos_angle = math.acos(cos)
    sin_angle = math.asin(sin)

    if cos_angle <= math.pi/2 and sin_angle >= 0 :
        angle = cos_angle
    elif cos_angle >= math.pi/2 and sin_angle >= 0 :
        angle =  cos_angle
    elif cos_angle >= math.pi/2 and sin_angle <= 0 :
        angle =  math.pi - sin_angle
    elif cos_angle <= math.pi/2 and sin_angle <= 0 :
        angle =  2*math.pi + sin_angle
    return angle
    
class M_func:
    def __init__(self, ecc, M=0):
        self.ecc = ecc
        self.M = M
    def __call__(self, E):
        return E + self.ecc * math.sin(E) - self.M
    
class M_prime(M_func):
    def __call__(self, E):
        return 1 + self.ecc * math.cos(E)
    
def get_E(M, ecc):
    '''M is mean_anomaly in radians!'''
    return newton(M_func(ecc, M), 1, fprime=M_prime(ecc, M))

def get_nu(E, ecc):
    cos_nu = (math.cos(E) - ecc) / (1 - ecc * math.cos(E))
    sin_nu = (math.sqrt(1 - ecc**2) * math.sin(E)) / (1 - ecc * math.cos(E))
    return get_angle(cos_nu, sin_nu)

def to_rad(deg):
    return deg * math.pi / 180.0

def to_deg(rad):
    return rad * 180.0 / math.pi

def write_packets(packets, destination):
    packets = [packet.to_json() for packet in packets]
    for packet in packets:
        for key, value in packet.items():
            packet[key] = str(value)


    packet_str = str(packets)
    packet_str = packet_str.replace("\\n","")
    packet_str = packet_str.replace(" ","")
    packet_str = packet_str.replace("'","\"")
    packet_str = packet_str.replace("\"{","{")
    packet_str = packet_str.replace("}\"","}")
    packet_str = packet_str.replace("True","true")
    packet_str = packet_str.replace("False","false")
    packet_str = packet_str.replace("("," [")
    packet_str = packet_str.replace(")","] ")
    packet_str = packet_str.replace(",]","]")
    packet_str = packet_str.replace("\"\"","\"")

    with open(destination, 'w') as file:
        file.write(packet_str)

def foundry_to_poliastro(orbitingObject):
    a = orbitingObject.semimajor_axis
    ecc = orbitingObject.eccentricity
    inc = orbitingObject.inclination
    argp = orbitingObject.arg_of_pericenter
    raan = orbitingObject.ra_of_asc_node
    mean_anomaly = orbitingObject.mean_anomaly
    epoch = orbitingObject.epoch

    # Get True Anomaly (nu)
    eccentric_anomaly = get_E(to_rad(mean_anomaly), ecc)
    nu = get_nu(eccentric_anomaly, ecc)
    nu = to_deg(nu)

    new_orbit = Orbit.from_classical(
        Earth,
        a = a << u.kilometer,
        ecc = ecc << u.one,
        inc= inc << u.deg,
        raan = raan << u.deg,
        argp=argp << u.deg, 
        nu=nu << u.deg,
        epoch=Time(epoch)
    )

    return new_orbit

def check_intersection(orb1, orb2, time_of_flight, time_step, threshold=0):
    """
    Checks for intersection between two orbits using numerical propagation.

    Args:
        orb1, orb2: poliastro.twobody.Orbit objects.
        time_of_flight: Total time to propagate.
        time_step: Time step for propagation (minutes).

    Returns:
        bool: True if intersection is likely, False otherwise.
    """

    t = 0
    max = int((time_of_flight / (1 * u.minute)).decompose())
    mod_step = int(time_step / u.minute)
    while (t < max):
        r1 = orb1.propagate(t * u.minute).r
        r2 = orb2.propagate(t * u.minute).r
        distance = np.linalg.norm(r1 - r2)
        if distance <= threshold:
            return True
        t += mod_step

    return False

def find_closest_pair(arr1, arr2):
    distances = cdist(arr1, arr2)
    min_distance = np.min(distances)
    return min_distance

def tuples_to_np(arr):
    arr = [np.array(list(x)) for x in arr]
    return np.stack(arr, axis=0)

def clean_arr_str(arr_str):
    arr_str = arr_str.replace(' [', '')
    arr_str = arr_str.replace('[', '')
    arr_str = arr_str.replace(']', '')
    arr_str = arr_str.replace('  ', ' ')
    return arr_str

def np_from_string(str):
    arr = np.fromstring(str, sep=' ')
    arr = arr.reshape(5000,3)
    return arr