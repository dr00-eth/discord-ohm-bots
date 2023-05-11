from datetime import datetime, timedelta
from enum import Enum

def get_token_record_7d_query():
    today = datetime.utcnow().date()
    date_7d_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    return {"query": f"{{tokenRecords( where: {{date_gt: \"{date_7d_ago}\"}}, orderBy: block, orderDirection: desc, first: 1000 ) {{ block valueExcludingOhm token isLiquid date }}}}"}

def get_token_supply_7d_query():
    today = datetime.utcnow().date()
    date_7d_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    return {"query": f"{{tokenSupplies( where: {{date_gt: \"{date_7d_ago}\"}}, orderBy: block, orderDirection: desc, first: 1000) {{ block type date supplyBalance tokenAddress source sourceAddress pool poolAddress }}}}"}

PRICE_UPDATE_INTERVAL = 20 # in minutes
GENERIC_UPDATE_INTERVAL = 10 # in minutes
LB_UPDATE_INTERVAL = 720 # in minutes
INDEX_UPDATE_INTERVAL = 360 # in minutes
ETH_SUBGRAPH_URL = 'https://gateway.thegraph.com/api/[api-key]/deployments/id/QmfC7nn4agkCjpgsjVdcCkKiKoGiu97yQTQSG1z7EaNnxd'
SUBGRAPH_URLS = (
    ETH_SUBGRAPH_URL,  # Ethereum, update above
    'https://api.thegraph.com/subgraphs/name/olympusdao/protocol-metrics-arbitrum',  # Arbitrum
    'https://api.thegraph.com/subgraphs/name/olympusdao/protocol-metrics-polygon',  # Polygon
    'https://api.thegraph.com/subgraphs/name/olympusdao/protocol-metrics-fantom'  # Fantom
)
BLOCK_REQUEST_QUERY = {"query": "{ tokenRecords(first: 1, orderBy: block, orderDirection: desc) { block }}"}
TOKEN_SUPPLY_QUERY = "{{tokenSupplies( where: {{block: \"{}\"}}) {{ type supplyBalance }}}}"
TOKEN_SUPPLY_7D_QUERY = get_token_supply_7d_query()
TOKEN_RECORD_QUERY = "{{tokenRecords( where: {{block: \"{}\"}}) {{ value valueExcludingOhm tokenAddress token isLiquid category multiplier }}}}"
TOKEN_RECORD_7D_QUERY = get_token_record_7d_query()
INDEX_PRICE_QUERY = "{{protocolMetrics(first: 1, where: {{block: \"{}\"}}) {{ currentIndex ohmPrice gOhmPrice }}}}"
STREAK_MESSAGE_SEQUENCE = ['earth', 'fire', 'wind', 'water', 'heart', 'go planet']
SCAMMER_KEYWORDS = ['mod', 'help desk', 'support', 'dev', 'mee6', 'shaft', 'relwyn', 'joel_', 'yattep', 'guerrillatrader', 'MEEE6',
                     'ầ', 'ợ', 'ị', '𝐂', '𝐚', '𝐩', '𝐭', '𝐡', '𝐎', '𝐦', '𝐲', '𝐮', '𝐥', '𝚕', '𝘴', '𝘶', '𝘱', '𝘖', '𝘺', '𝐎', 'hohmward',
                     'Z|Range, Bound|', 'Wartull', 'spoys P', 'Hermes', 'ReIwyn', 'gueriIIatrader', 'WartuII', 'joeI_', 'support ticket',
                     'mee6', 'sentinel', 'support', 'dr00', 'drOO', 'zeus']
##Excluded IDs (IN ORDER) Dr00, yattep, Z. hohmward, relwyn, guerillatrader,
##                        shaft, wartull, zeus, apollonius, joel, spoys P,
##                        mee6 bot, sentinel bot, hermes bot
EXCLUDE_IDS= [828736415013404702, 526240486822903818, 855229180567355422, 894321349210820618, 215990494197448704, 883022147742752820,
              804035483494645771, 299261433961512960, 383712533300641793, 407997042816974848, 220200518834716673, 915007255655612496,
              159985870458322944, 985951550667128863, 470723870270160917]
EXCLUDE_COMM_IDS = []
ADMIN_ROLE = "Scholars"
INTERN_ROLE = "Intern"
GRASSHOPPER = "Grasshoppers"
DATE_FORMAT = '%m/%d %-I:%M%p'
LOG_CHANNEL = 825084057700139049
GENERAL_CHANNEL = 823623103874990091
OT_CHANNEL = 798371943324844042
LEARN_CHANNEL = 817567648451133461
EXPIRATION = 120

class DataType(Enum):
    TOKEN_RECORDS = 'tokenRecords'
    TOKEN_SUPPLIES = 'tokenSupplies'

class TokenType(Enum):
    TYPE_BONDS_DEPOSITS = "OHM Bonds (Burnable Deposits)"
    TYPE_BONDS_PREMINTED = "OHM Bonds (Pre-minted)"
    TYPE_BONDS_VESTING_DEPOSITS = "OHM Bonds (Vesting Deposits)"
    TYPE_BONDS_VESTING_TOKENS = "OHM Bonds (Vesting Tokens)"
    TYPE_BOOSTED_LIQUIDITY_VAULT = "Boosted Liquidity Vault"
    TYPE_LENDING = "Lending"
    TYPE_LIQUIDITY = "Liquidity"
    TYPE_OFFSET = "Manual Offset"
    TYPE_TOTAL_SUPPLY = "Total Supply"
    TYPE_TREASURY = "Treasury"

class GOhm(Enum):
    NETWORK_MAINNET = "0x0ab87046fBb341D058F17CBC4c1133F25a20a52f"
    NETWORK_ARBITRUM = "0x8D9bA570D6cb60C7e3e0F31343Efe75AB8E65FB1"
    NETWORK_POLYGON = "0xd8cA34fd379d9ca3C6Ee3b3905678320F5b45195"
    NETWORK_FANTOM = "0x91fa20244fb509e8289ca630e5db3e9166233fdc"

class Ohm(Enum):
    NETWORK_MAINNET = "0x64aa3364f17a4d01c6f1751fd97c2bd3d7e7f1d5"