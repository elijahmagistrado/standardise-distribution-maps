import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def name_match(merged, sci_name):
    # Name matching records with API
    class_api = "https://namematching-ws.ala.org.au/api/searchByClassification"
    name_list = merged[f'{sci_name}'].tolist()
    family_list = []

    def make_request(name):
        with requests.get(class_api, params={'scientificName': {name}}) as match:
            return match.json(), name

    with ThreadPoolExecutor() as executor:
        good_matches = []
        unsuccessful = []
        bad_matches = []
        futures = {executor.submit(make_request, name): name for name in name_list}
        for future in as_completed(futures):
            result = future.result()
            data, name = result
            if data['success']:
                if data['matchType'] == 'exactMatch' or data['matchType'] == 'canonicalMatch':
                    if data['rank'] == 'species' or data['rank'] == 'subspecies':
                        good_matches.append(name)
                        family_list.append(data['family'].upper())
                else:
                    bad_matches.append(name)
            else:
                unsuccessful.append(name)

    if len(merged) != len(good_matches):
        valid_records = merged[merged[f'{sci_name}'].isin(good_matches)].reset_index(drop=True)
        invalid_records = merged[~merged[f'{sci_name}'].isin(good_matches)].reset_index(drop=True)
        print(f'{len(invalid_records)} low quality record(s) removed.'
              f'{len(unsuccessful)} species not found in the ALA.'
              f'{len(bad_matches)} bad matches with ALA taxonomy.')
        valid_records = valid_records
    else:
        valid_records = merged

    return valid_records, family_list
