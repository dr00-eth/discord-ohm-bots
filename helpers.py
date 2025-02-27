from constants import GOhm
import requests
import constants
from constants import TokenType, GOhm, Ohm
import json
import io
import numpy as np
import os
from datetime import datetime
# HELPERS


def get_data(url, queryFormat, construct=False):
    if construct:
        query = {"query": queryFormat.format(get_latest_block(url))}
    else:
        query = queryFormat

    # Replace the API key if present in the URL
    api_key = os.environ.get('SUBGRAPH_API_KEY')
    if api_key and "[api-key]" in url:
        url = url.replace('[api-key]', api_key)

    raw = requests.post(url, json=query)
    raw_json = json.loads(raw.text)
    return raw_json


def get_latest_block(url):
    data = get_data(url, constants.BLOCK_REQUEST_QUERY)
    return data['data']['tokenRecords'][0]['block']


def get_image_data(image_url):
    response = requests.get(image_url)
    image_bytes = io.BytesIO(response.content)
    return image_bytes


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    if magnitude == 0:
        return '${:.2f}'.format(num)
    elif num.is_integer():
        return '${:.0f}{}'.format(num, ['', 'K', 'M', 'B', 'T'][magnitude])
    else:
        return '${:.1f}{}'.format(num, ['', 'K', 'M', 'B', 'T'][magnitude])


def check_outlier(data):
    sorted_data = sorted(data.values())

    median = np.median(sorted_data)
    mad = np.median([np.abs(value - median) for value in sorted_data])

    mad_lower_bound = median - 15 * mad
    mad_upper_bound = median + 15 * mad
    print(f'Upper bound: {mad_upper_bound}')
    print(f'Lower bound: {mad_lower_bound}')

    deleted_items = []
    for date, value in list(data.items()):
        if value < mad_lower_bound or value > mad_upper_bound:
            print(f'Removing: {data[date]}')
            deleted_items.append((date, data[date]))
            del data[date]

    return data, deleted_items, mad_upper_bound, mad_lower_bound


def get_records_with_highest_block(data, data_type):
    if data_type == constants.DataType.TOKEN_RECORDS:
        data_records = data['data'][constants.DataType.TOKEN_RECORDS.value]

    if data_type == constants.DataType.TOKEN_SUPPLIES:
        data_records = data['data'][constants.DataType.TOKEN_SUPPLIES.value]
    records_by_date = {}
    for record in data_records:
        date = record['date']
        if date not in records_by_date:
            records_by_date[date] = []
        records_by_date[date].append(record)

    records_with_highest_block = []
    for date, records in records_by_date.items():
        highest_block = max([int(record['block']) for record in records])
        records_with_highest_block.extend(
            [record for record in records if int(record['block']) == highest_block])

    return records_with_highest_block


def aggregate_tkn_vals(data):
    aggregated_data = {}

    # loop through the tokenRecords (pre-cleansed) array
    for token_record in data:
        # check if the liquid"
        if token_record['isLiquid'] == True:
            # convert the value string to a float
            token_value = float(token_record['valueExcludingOhm'])
            date = token_record['date']
            # add the token (excluding OHM) value to the aggregated data for the date
            aggregated_data[date] = aggregated_data.get(date, 0) + token_value

  # return the sum of supplyBalance values for each date
    return aggregated_data


def get_price_ohm():
    data = get_data(constants.ETH_SUBGRAPH_URL,
                    constants.INDEX_PRICE_QUERY, True)

    return float(data["data"]["protocolMetrics"][0]["ohmPrice"])


def get_price_gohm():
    data = get_data(constants.ETH_SUBGRAPH_URL,
                    constants.INDEX_PRICE_QUERY, True)

    return float(data["data"]["protocolMetrics"][0]["gOhmPrice"])

def get_supply_data(url, include_types):
    data = get_data(url, constants.TOKEN_SUPPLY_QUERY, True)
    tokens = get_records_with_highest_block(data, constants.DataType.TOKEN_SUPPLIES)

    # Filter tokens based on the provided inclusion lists, if they are not None
    if include_types is not None:
        tokens = list(
            filter(lambda x: x['type'] in include_types, tokens))
        supply = sum(
            float(tkn['supplyBalance']) * get_token_multiplier(tkn['tokenAddress']) for tkn in tokens)
    else:
        supply = 0

    return supply


def get_circulating_supply():
    # Define the types of tokens to include for calculating the circulating supply
    include_types_circulating = [TokenType.TYPE_TOTAL_SUPPLY.value, TokenType.TYPE_TREASURY.value, TokenType.TYPE_OFFSET.value, TokenType.TYPE_BONDS_PREMINTED.value,
                                 TokenType.TYPE_BONDS_VESTING_DEPOSITS.value, TokenType.TYPE_BONDS_DEPOSITS.value, TokenType.TYPE_BOOSTED_LIQUIDITY_VAULT.value]

    # Initialize the total circulating supply
    total_circulating_supply = 0

    # Iterate over the subgraph URLs and calculate the total circulating supply
    for url in constants.SUBGRAPH_URLS:
        # Get supply data for each subgraph URL
        circulating_supply = get_supply_data(
            url, include_types_circulating)
        total_circulating_supply += circulating_supply

    return total_circulating_supply


def get_floating_supply():
    # Define the types of tokens to include for calculating the floating supply
    include_types_floating = [TokenType.TYPE_TOTAL_SUPPLY.value, TokenType.TYPE_TREASURY.value, TokenType.TYPE_OFFSET.value, TokenType.TYPE_BONDS_PREMINTED.value,
                              TokenType.TYPE_BONDS_VESTING_DEPOSITS.value, TokenType.TYPE_BONDS_DEPOSITS.value, TokenType.TYPE_BOOSTED_LIQUIDITY_VAULT.value, TokenType.TYPE_LIQUIDITY.value]

    # Initialize the total floating supply
    total_floating_supply = 0

    # Iterate over the subgraph URLs and calculate the total floating supply
    for url in constants.SUBGRAPH_URLS:
        # Get supply data for each subgraph URL
        floating_supply = get_supply_data(url, include_types_floating)
        total_floating_supply += floating_supply

    return total_floating_supply

def get_backed_supply():
    # Define the types of tokens to include for calculating the backed supply
    include_types_backed = [TokenType.TYPE_TOTAL_SUPPLY.value, TokenType.TYPE_TREASURY.value, TokenType.TYPE_OFFSET.value, TokenType.TYPE_BONDS_PREMINTED.value, TokenType.TYPE_BONDS_VESTING_DEPOSITS.value, TokenType.TYPE_BONDS_DEPOSITS.value, TokenType.TYPE_BOOSTED_LIQUIDITY_VAULT.value, TokenType.TYPE_LIQUIDITY.value, TokenType.TYPE_LENDING.value]

    # Initialize the total backed supply
    total_backed_supply = 0

    # Iterate over the subgraph URLs and calculate the total backed supply
    for url in constants.SUBGRAPH_URLS:
        # Get supply data for each subgraph URL (circulating supply is not needed here)
        backed_supply = get_supply_data(url, include_types_backed)

        total_backed_supply += backed_supply

    return total_backed_supply


def get_raw_index():
    data = get_data(constants.ETH_SUBGRAPH_URL,
                    constants.INDEX_PRICE_QUERY, True)

    return data["data"]["protocolMetrics"][0]["currentIndex"]


def get_lb_total():
    # Initialize the total liquid balance
    total_lb = 0

    # Iterate over the subgraph URLs and calculate the total liquid balance
    for url in constants.SUBGRAPH_URLS:
        data = get_data(url, constants.TOKEN_RECORD_QUERY, True)
        # Cleanse to remove extra blocks per day
        data = get_records_with_highest_block(
            data, constants.DataType.TOKEN_RECORDS)
        # Filter tokens that are marked as liquid
        liq_tkns = list(filter(lambda x: x['isLiquid'] == True, data))
        # Sum the valueExcludingOhm for the liquid tokens and add to the total
        total_lb += sum(float(t['valueExcludingOhm']) for t in liq_tkns)

    # Return the combined total liquid balance
    return total_lb


def get_token_multiplier(token):
    # Check if the provided token address is one of the addresses defined in the GOhm class
    if token.lower() in (gohm.value.lower() for gohm in GOhm):
        # Define the multiplier for the token (replace 1.0 with the actual multiplier value)
        multiplier = get_raw_index()
        return float(multiplier)
    else:
        return float(1)


def get_current_day_lb():

    # Initialize the total backed supply
    total_backed_supply = get_backed_supply()

    # Calculate the combined token values
    combined_token_vals = get_lb_total()

    # Calculate the current day lb
    return combined_token_vals / total_backed_supply

def check_errors(data):
    if 'errors' in data:
        return True
    return False

def get_7d_backed_supply():
    # Define the types of tokens to include for calculating the backed supply
    include_types_backed = [TokenType.TYPE_TOTAL_SUPPLY.value, TokenType.TYPE_TREASURY.value, TokenType.TYPE_OFFSET.value, TokenType.TYPE_BONDS_PREMINTED.value, TokenType.TYPE_BONDS_VESTING_DEPOSITS.value, TokenType.TYPE_BONDS_DEPOSITS.value, TokenType.TYPE_BOOSTED_LIQUIDITY_VAULT.value, TokenType.TYPE_LIQUIDITY.value, TokenType.TYPE_LENDING.value]

    # Create a dictionary to store the sum of supplyBalance values for each date
    aggregated_data = {}
    # Variable to store the highest date from the first iteration (Mainnet)
    highest_date = None

    # Iterate over the subgraph URLs and calculate the 7-day backed supply for each network
    for index, url in enumerate(constants.SUBGRAPH_URLS):
        data = get_data(url, constants.get_token_supply_7d_query())

        # Subgraph sometimes errors, print and skip
        if check_errors(data):
            print(f"Error fetching data from {url}")
            continue

        # Get data from the highest block per day to eliminate partial indexing
        data = get_records_with_highest_block(
            data, constants.DataType.TOKEN_SUPPLIES)

        # Create a set to keep track of unique dates in the current iteration
        current_dates = set()
        # Loop through the tokenSupplies array
        for token_supply in data:
            # Check if the type is in the include_types_backed list above
            if token_supply['type'] in include_types_backed:
                # Convert the supplyBalance string to a float and check if gOHM for multiplier
                supply_balance = float(
                    token_supply['supplyBalance']) * get_token_multiplier(token_supply['tokenAddress'])
                date = token_supply['date']
                # Add the supplyBalance value to the aggregated data for the date
                aggregated_data[date] = aggregated_data.get(
                    date, 0) + supply_balance
                # Add the date to the current_dates set
                current_dates.add(date)

        # If this is the first iteration, store the highest date for mainnet
        if index == 0:
            highest_date = max(current_dates)
        # If this is the second iteration, check if the highest date is present
        elif index == 1 and highest_date not in current_dates:
            # Remove the highest date from the aggregated data
            aggregated_data.pop(highest_date, None)

    # Return the sum of supplyBalance values for each date
    return aggregated_data


def get_7d_token_values():
    # Create a dictionary to store the sum of token values for each date
    aggregated_result = {}

    # Iterate over the subgraph URLs and calculate the 7-day token values
    for url in constants.SUBGRAPH_URLS:
        data = get_data(url, constants.get_token_record_7d_query())
        # Cleanse to remove extra blocks per day
        data = get_records_with_highest_block(
            data, constants.DataType.TOKEN_RECORDS)
        # Aggregate token values for the current subgraph
        current_result = aggregate_tkn_vals(data)
        # Merge the current result into the aggregated result
        for date, value in current_result.items():
            if date in aggregated_result:
                aggregated_result[date] += value
            else:
                aggregated_result[date] = value

    # Return the combined 7-day token values
    return aggregated_result


def get_7d_lb_sma():
  # Get the necessary values to determine Liquid Backing per Backed OHM
    agg_token_values = get_7d_token_values()
    agg_token_supplies = get_7d_backed_supply()

  # Divide Treasury Liquid Backing by Backed OHM Supply, per day
    result = {}
    for currdate, value1 in agg_token_values.items():
        try:
            value2 = agg_token_supplies[currdate]
            result[currdate] = value1 / value2
        except KeyError:
            # Skip this iteration if the date is not present in the second array
            continue
    result, removed, upper, lower = check_outlier(result)
  # Get the 7 day SMA
    sum_of_values = sum(result.values())
    average = sum_of_values / len(result)

    return average, removed, upper, lower


def get_7d_lb_sma_raw():
  # Get the necessary values to determine Liquid Backing per Backed OHM
    agg_values = get_7d_token_values()
    agg_token_supplies = get_7d_backed_supply()

  # Divide Treasury Liquid Backing by Backed OHM Supply, per day
    result = {}
    for currdate, value1 in agg_values.items():
        try:
            value2 = agg_token_supplies[currdate]
            result[currdate] = value1 / value2
        except KeyError:
            # Skip this iteration if the date is not present in the second array
            continue

    return result
