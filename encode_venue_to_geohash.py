import collections
import numpy as np
import random
import pandas as pd
import pickle
import proximitypyhash
import pygeohash as pgh

city = 'chicago'

# Pseudo path where the data is saved.
folder_path = '/path/to/data/'

# Loads all venues from Foursquare dataset.
all_venues = pd.read_pickle(folder_path + city + "_venue_info_v2.pkl")

# Creates a dictionary from venue_id to index for easy venue search in later stages.
venue_id_to_idx = {}
for idx, record in all_venues.iterrows():
    venue_id_to_idx[record['id']] = idx

# Saves the dictionary for later usage.
f = open(folder_path + city + '_venue_id_to_idx.pkl', "wb")
pickle.dump(venue_id_to_idx, f)
f.close()

# Encodes each venue's coordinate as geohash, and saves it a dictionary from geohash to a list of venue_ids
# https://github.com/dice89/proximityhash
prec = 8
geohash_to_venue_ids = collections.defaultdict(list)
for idx, record in all_venues.iterrows():
    geohash = pgh.encode(record['lat'], record['lng'], precision=prec)
    geohash_to_venue_ids[geohash].append(record['id'])

# Saves the dictionary for later usage.
f = open(folder_path + city + '_geohash_to_venue_ids_' + str(prec) + '.pkl', "wb")
pickle.dump(geohash_to_venue_ids, f)
f.close()

# A prepared dictionary for business venues only. The key is the venue_ids, and the value is the venue rating.
venue_id_to_rating = pd.read_pickle(folder_path + city + '_venue_id_to_rating.pkl')

# Encodes each venue's coordinate as geohash, and saves it a dictionary from geohash to a list of venue_ids
# https://github.com/dice89/proximityhash
# geohash_to_venue_ids_b is for business venues
geohash_to_venue_ids_b = collections.defaultdict(list)
# geohash_to_venue_ids_nb is for non-business venues
geohash_to_venue_ids_nb = collections.defaultdict(list)
for idx, record in all_venues.iterrows():
    geohash = pgh.encode(record['lat'], record['lng'], precision=prec)
    if record['id'] in venue_id_to_rating:
        geohash_to_venue_ids_b[geohash].append(record['id'])
    else:
        geohash_to_venue_ids_nb[geohash].append(record['id'])

# Saves the dictionary for later usage.
f = open(folder_path + city + '_geohash_to_venue_ids_b_' +str(prec)+ '.pkl', "wb")
pickle.dump(geohash_to_venue_ids_b, f)
f.close()
