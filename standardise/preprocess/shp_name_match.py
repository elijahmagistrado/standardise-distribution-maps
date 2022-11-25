import pandas as pd
import asyncio
import aiohttp


def name_match(merged, sci_name):
    # Name matching records with API
    api_link = "https://namematching-ws.ala.org.au/api/searchByClassification"

    # Function that sends individual get request
    async def submit_request(session, name):
        async with session.get(api_link, params={'scientificName': name}) as req:
            return name, await req.json()

    # Creates a list of tasks then executes all simultaneously
    async def submit_all_requests(session, name_list):
        tasks = []
        for name in name_list:
            task = asyncio.create_task(submit_request(session, name))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
        return res

    # Sends the species names to be submitted to the API
    async def send_names():
        name_list = merged[sci_name].tolist()

        async with aiohttp.ClientSession() as session:
            data = await submit_all_requests(session, name_list)
            return data

    # Command that executes and receives data from async calls
    api_data = asyncio.run(send_names())

    matched_list = pd.DataFrame()
    good_matches = []
    insufficient_level = []
    bad_matches = []
    not_found = []

    # Sorting out species by quality of name match
    for item in api_data:
        sp_name, sp_info = item

        if sp_info['success']:
            if sp_info['matchType'] in ['exactMatch', 'canonicalMatch']:
                if sp_info['rank'] in ['species', 'subspecies']:
                    if 'family' in sp_info:
                        good_matches.append(sp_name)
                        data_df = pd.DataFrame({"species": [sp_name], "family": [sp_info['family']]})
                        matched_list = pd.concat([matched_list, data_df])
                else:
                    insufficient_level.append(sp_name)
            else:
                bad_matches.append(sp_name)
        else:
            not_found.append(sp_name)

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
        print(f'All {len(merged)} records are valid.')

    return valid_records, matched_list
