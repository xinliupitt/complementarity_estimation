import argparse
import collections
import numpy as np
import random
from random import choice as random_choice
from random import choices as random_choices
from random import uniform as random_uniform
import os
import pandas as pd
import pickle
import proximitypyhash
import pygeohash as pgh
import time

city = 'chicago'
period = 'morning'
# Pseudo path where the data is saved.
folder_path = '/path/to/data/'
# Total number of movements in the simulation. We may change it to match the
# number of movements in the real-world data.
num_movements = 10000
# Number of completed movements in the simulation
done_movement_count = 0

start_moment = time.time()

city_venues = pd.read_pickle(folder_path + city + "_venue_info_v2.pkl")
venue_id_to_idx = pd.read_pickle(folder_path + city + '_venue_id_to_idx.pkl')
real_world_distances = pd.read_pickle(folder_path + city + period + '_distances_rating_impute.pkl')
venue_to_rating = pd.read_pickle(folder_path + city + '_venue_id_TO_rating_impute.pkl')
venue_b_to_rating = pd.read_pickle(folder_path + city + '_venue_id_TO_rating.pkl')

prec_to_geohash_b = {}
prec_to_geohash_nb = {}
prec = 8
geohash_to_venue_ids = pd.read_pickle(folder_path + city + '_geohash_to_venue_ids_b_' + str(prec) + '.pkl')
prec_to_geohash_b[prec] = geohash_to_venue_ids
geohash_to_venue_ids = pd.read_pickle(folder_path + city + '_geohash_to_venue_ids_nb_' + str(prec) + '.pkl')
prec_to_geohash_nb[prec] = geohash_to_venue_ids

venue_ids = list(venue_id_to_idx.keys())
venue_ids_b = list(venue_b_to_rating.keys())
venue_ids_nb = list(set(venue_id_to_idx) - set(venue_b_to_rating))
start_id = random_choice(venue_ids)
venues_to_save = [['J', start_id]]
linear_model = lambda x: x

# "B" means this venue is business.
# "NB" means this venue is non-business.
start_B = "B"
end_B = "B"

print('start venue business?', start_B == "B")
print('end venue business?', end_B == "B")
    
while done_movement_count < num_movements:
    if start_B == 'B':
        start_id = random_choice(venue_ids_b)
    else:
        start_id = random_choice(venue_ids_nb)
    # 'S' means start venue of this movement.
    venues_to_save.append(['S', start_id])

    idx = venue_id_to_idx[start_id]
    lat = city_venues.iloc[idx, :]['lat']
    lng = city_venues.iloc[idx, :]['lng']

    # Samples a distance to generate a ring area later
    sampled_distance = random_choice(real_world_distances)

    # All venues in the small circle
    small_locs = proximitypyhash.get_geohash_radius_approximation(latitude=lat, longitude=lng, radius=sampled_distance+500, precision=prec)
    # All venues in the large circle
    large_locs = proximitypyhash.get_geohash_radius_approximation(latitude=lat, longitude=lng, radius=sampled_distance+1000, precision=prec)
    small_set = set(small_locs)
    large_set = set(large_locs)
    # The difference of the large and the small circle is the ring area.
    ring_set = large_set - small_set
    # Identify all candidate venues in the ring area
    candidates = []
    for geoh in ring_set:
        if end_B == 'B':
            geohash_to_venue_ids = prec_to_geohash_b[prec]
        else:
            geohash_to_venue_ids = prec_to_geohash_nb[prec]
        if geoh in geohash_to_venue_ids:
            candidates += geohash_to_venue_ids[geoh]
    num_candidates = len(candidates)
    print('# candidates:', num_candidates)
    rating_to_venues = collections.defaultdict(list)
    for cand_venue in candidates:
        if cand_venue == start_id:
            continue
        rating = venue_to_rating[cand_venue]
        rating_to_venues[rating].append(cand_venue)
    rating_set = set(rating_to_venues.keys())
    ratings = list(rating_set)
    probs = []
    for rating in ratings:
        probs.append(linear_model(rating))
    # Sample a venue according to rating. The high rating a venue has, the higher probability for it to be sampled.
    sampled_ratings = random_choices(ratings, probs)
    sampled_rating = sampled_ratings[0]
    # The venue selected as the end venue of this movement.
    final_venues = rating_to_venues[sampled_rating]
    print('# rating candidates:', len(final_venues))
    start_id = random_choice(final_venues)
    # 'E' means end venue of this movement.
    venues_to_save.append(['E', start_id])
    done_movement_count += 1
    break

file_name = folder_path + city + '_simulated_venues_' + period + '_' + start_B + '_' + end_B + '.pkl'
os.makedirs(os.path.dirname(file_name), exist_ok=True)
f = open(file_name, "wb")
pickle.dump(venues_to_save, f)
f.close()

end_moment = time.time()
print('Run time:', end_moment-start_moment)
