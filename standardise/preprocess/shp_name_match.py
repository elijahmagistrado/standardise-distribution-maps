import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def name_match(merged, sci_name):
    # Name matching records with API
    api_link = "https://namematching-ws.ala.org.au/api/searchByClassification"
    name_list = merged[sci_name].tolist()      # List of species names to submit to the API

    # Function used for sending API request
    def make_request(name):
        with requests.get(api_link, params={'scientificName': name}) as match:
            return match.json(), name

    # Submitting multiple requests simultaneously using threading
    with ThreadPoolExecutor() as executor:
        good_matches = []
        not_found = []              # Species not found in the ALA taxonomy
        bad_matches = []            # Not exact or canonical matches
        insufficient_level = []     # Not down to species or subspecies level

        matched_list = pd.DataFrame()

        futures = {executor.submit(make_request, name): name for name in name_list}
        for future in as_completed(futures):
            result = future.result()
            data, name = result

            # Filtering and classifying results based on their validity
            if data['success']:
                if data['matchType'] in ['exactMatch', 'canonicalMatch']:
                    if data['rank'] in ['species', 'subspecies']:
                        if 'family' in data:
                            good_matches.append(name)
                            data_df = pd.DataFrame({"species": [name], "family": [data['family']]})
                            matched_list = pd.concat([matched_list, data_df])
                    else:
                        insufficient_level.append(name)
                else:
                    bad_matches.append(name)
            else:
                not_found.append(name)

    # Filtering invalid records from merged GeoDataFrame
    if len(merged) != len(good_matches):
        valid_records = merged[merged[sci_name].isin(good_matches)].reset_index(drop=True)
        invalid_records = merged[~merged[sci_name].isin(good_matches)].reset_index(drop=True)

        # Printing out details about removed records
        print(f'{len(invalid_records)} low quality record(s) removed.')
        print(f'{len(not_found)} species not found in the ALA:')
        print(not_found)
        print(f'{len(bad_matches)} bad matches with ALA taxonomy:')
        print(bad_matches)
        print(f'{len(insufficient_level)} record(s) not down to species or subspecies level:')
        print(insufficient_level)

    else:
        valid_records = merged

    return valid_records, matched_list
