from quant_core.exceptions.exceptions import EpicNotFoundError

EPIC_TO_POLYGON_CRYPTO_DICTIONARY = {
    "CS.D.ETHUSD.CFD.IP": "ETHUSD",
    "CS.D.AVXUSD.CFD.IP": "AVAXUSD",
    "CS.D.ADAUSD.CFD.IP": "ADAUSD",
}

EPIC_TO_POLYGON_FOREX_DICTIONARY = {
    "CS.D.USDCHF.MINI.IP": "USDCHF",
    "CS.D.EURGBP.MINI.IP": "EURGBP",
}

EPIC_TO_POLYGON_DICTIONARY = {**EPIC_TO_POLYGON_CRYPTO_DICTIONARY, **EPIC_TO_POLYGON_FOREX_DICTIONARY}

POLYGON_TO_EPIC_DICTIONARY = {v: k for k, v in EPIC_TO_POLYGON_DICTIONARY.items()}


class DataBroker:
    def convert_epic_to_polygon(self, epic: str) -> str:
        if polygon_symbol := EPIC_TO_POLYGON_DICTIONARY.get(epic):
            return polygon_symbol

        raise EpicNotFoundError(epic)
