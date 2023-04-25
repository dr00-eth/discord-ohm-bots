import requests
import constants
import json
import io
import numpy as np
import os
from datetime import datetime
## HELPERS

def get_data(url, queryFormat, construct = False):
    if construct:
        query = { "query": queryFormat.format(get_latest_block(url)) }
    else:
        query = queryFormat
    ## TODO: will need to update this logic if other endpoints have diff keys
    if "[api-key]" in url:
        url = url.replace('[api-key]', os.environ['SUBGRAPH_API_KEY'])
    raw = requests.post(url, json = query)
    raw_json = json.loads(raw.text)
    return raw_json

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
        records_with_highest_block.extend([record for record in records if int(record['block']) == highest_block])

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

def get_latest_block(url):
    if url == constants.SUBGRAPH_URL:
      data = get_data(constants.SUBGRAPH_URL, constants.BLOCK_REQUEST_QUERY)
    elif url == constants.ARBI_SUBGRAPH_URL:
      data = get_data(constants.ARBI_SUBGRAPH_URL, constants.BLOCK_REQUEST_QUERY)
    elif url == constants.POLY_SUBGRAPH_URL:
      data = get_data(constants.POLY_SUBGRAPH_URL, constants.BLOCK_REQUEST_QUERY)
    else:
      data = get_data(constants.FTM_SUBGRAPH_URL, constants.BLOCK_REQUEST_QUERY)
    
    return data['data']['tokenRecords'][0]['block']

def get_price_ohm():
    data = get_data(constants.SUBGRAPH_URL, constants.INDEX_PRICE_QUERY, True)
    
    return float(data["data"]["protocolMetrics"][0]["ohmPrice"])

def get_price_gohm():
    data = get_data(constants.SUBGRAPH_URL, constants.INDEX_PRICE_QUERY, True)
    
    return float(data["data"]["protocolMetrics"][0]["gOhmPrice"])

def get_circulating_supply():
    data = get_data(constants.SUBGRAPH_URL,constants.TOKEN_SUPPLY_QUERY, True)
    tokens = data['data']['tokenSupplies']
    non_liq_tkns = list(filter(lambda x: x['type'] != "Liquidity" and x['type'] != "Lending" and x['type'] != "OHM Bonds (Vesting Tokens)", tokens))
    
    return sum(float(tkn['supplyBalance']) for tkn in non_liq_tkns)

def get_floating_supply():
    data = get_data(constants.SUBGRAPH_URL,constants.TOKEN_SUPPLY_QUERY, True)
    tokens = data['data']['tokenSupplies']
    tokens = list(filter(lambda x: x['type'] != "OHM Bonds (Vesting Tokens)", tokens))
    
    return sum(float(tkn['supplyBalance']) for tkn in tokens)

def get_raw_index():
    data = get_data(constants.SUBGRAPH_URL, constants.INDEX_PRICE_QUERY, True)
    
    return data["data"]["protocolMetrics"][0]["currentIndex"]

def get_lb_total_eth():
    data = get_data(constants.SUBGRAPH_URL,constants.TOKEN_RECORD_QUERY, True)

    tokens = data['data']['tokenRecords']
    liq_tkns = list(filter(lambda x: x['isLiquid'] == True, tokens))
    return sum(float(t['valueExcludingOhm']) for t in liq_tkns)

def get_lb_total_arbi():
    data = get_data(constants.ARBI_SUBGRAPH_URL,constants.TOKEN_RECORD_QUERY, True)

    tokens = data['data']['tokenRecords']
    liq_tkns = list(filter(lambda x: x['isLiquid'] == True, tokens))
    return sum(float(t['valueExcludingOhm']) for t in liq_tkns)

def get_lb_total_poly():
    data = get_data(constants.POLY_SUBGRAPH_URL,constants.TOKEN_RECORD_QUERY, True)

    tokens = data['data']['tokenRecords']
    liq_tkns = list(filter(lambda x: x['isLiquid'] == True, tokens))
    return sum(float(t['valueExcludingOhm']) for t in liq_tkns)

def get_lb_total_ftm():
    data = get_data(constants.FTM_SUBGRAPH_URL,constants.TOKEN_RECORD_QUERY, True)

    tokens = data['data']['tokenRecords']
    liq_tkns = list(filter(lambda x: x['isLiquid'] == True, tokens))
    return sum(float(t['valueExcludingOhm']) for t in liq_tkns)

def get_combined_lb_total():
    return get_lb_total_eth() + get_lb_total_arbi() + get_lb_total_poly() + get_lb_total_ftm()

def get_current_day_lb():
    combined_token_vals = get_combined_lb_total()
    floating_supply = get_floating_supply()

    return combined_token_vals / floating_supply

def get_7d_floating_supply():
    data = get_data(constants.SUBGRAPH_URL,constants.get_token_supply_7d_query())
  # get data from highest block per day
    data = get_records_with_highest_block(data, constants.DataType.TOKEN_SUPPLIES)
  # create a dictionary to store the sum of supplyBalance values for each date
    aggregated_data = {}
    
    # loop through the tokenSupplies array
    for token_supply in data:
        # check if the type is not "OHM Bonds (Vesting Tokens)"
        if token_supply['type'] != "OHM Bonds (Vesting Tokens)":
            # convert the supplyBalance string to a float
            supply_balance = float(token_supply['supplyBalance'])
            date = token_supply['date']
            # add the supplyBalance value to the aggregated data for the date
            aggregated_data[date] = aggregated_data.get(date, 0) + supply_balance

  # return the sum of supplyBalance values for each date
    return aggregated_data


def get_7d_eth_token_values():
    data = get_data(constants.SUBGRAPH_URL,constants.get_token_record_7d_query())
  # cleanse to remove extra blocks per day
    data = get_records_with_highest_block(data, constants.DataType.TOKEN_RECORDS)
  # return the sum of supplyBalance values for each date
    return aggregate_tkn_vals(data)

def get_7d_arbi_token_values():
    data = get_data(constants.ARBI_SUBGRAPH_URL,constants.get_token_record_7d_query())
  # cleanse to remove extra blocks per day
    data = get_records_with_highest_block(data, constants.DataType.TOKEN_RECORDS)
  # return the sum of supplyBalance values for each date
    return aggregate_tkn_vals(data)


def get_7d_poly_token_values():
    data = get_data(constants.POLY_SUBGRAPH_URL,constants.get_token_record_7d_query())
  # cleanse to remove extra blocks per day
    data = get_records_with_highest_block(data, constants.DataType.TOKEN_RECORDS)
  # return the sum of supplyBalance values for each date
    return aggregate_tkn_vals(data)


def get_7d_ftm_token_values():
    data = get_data(constants.FTM_SUBGRAPH_URL,constants.get_token_record_7d_query())
  # cleanse to remove extra blocks per day
    data = get_records_with_highest_block(data, constants.DataType.TOKEN_RECORDS)
  # return the sum of supplyBalance values for each date
    return aggregate_tkn_vals(data)

def get_7d_agg_token_values():
    result1 = get_7d_eth_token_values()
    result2 = get_7d_arbi_token_values()
    result3 = get_7d_poly_token_values()
    result4 = get_7d_ftm_token_values()
    # create a dictionary to store the sum of supplyBalance values for each date
    aggregated_result = {}
    for res in [result1, result2, result3, result4]:
        for date, value in res.items():
            if date in aggregated_result:
                aggregated_result[date] += value
            else:
                aggregated_result[date] = value
            
    return aggregated_result

def get_7d_lb_sma():
  # Get the necessary values to determine Liquid Backing per Floating OHM
    agg_values = get_7d_agg_token_values()
    agg_supplies = get_7d_floating_supply()

  # Divide Treasury Liquid Backing by Floating OHM Supply, per day 
    result = {}
    for currdate, value1 in agg_values.items():
        try:
            value2 = agg_supplies[currdate]
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
  # Get the necessary values to determine Liquid Backing per Floating OHM
    agg_values = get_7d_agg_token_values()
    agg_supplies = get_7d_floating_supply()

  # Divide Treasury Liquid Backing by Floating OHM Supply, per day 
    result = {}
    for currdate, value1 in agg_values.items():
        try:
            value2 = agg_supplies[currdate]
            result[currdate] = value1 / value2
        except KeyError:
            # Skip this iteration if the date is not present in the second array
            continue

    return result