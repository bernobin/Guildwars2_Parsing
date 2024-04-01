from PARSING.Cerus_Parser import CerusParser
from PARSING.QadimThePeerless_Parser import QadimThePeerlessParser
from PARSING.Qadim_Parser import QadimParser
from PARSING.Samarog_Parser import SamarogParser


def parser_factory(boss):
    match boss:
        case "Cerus":
            return CerusParser()
        case "Qadim":
            return QadimParser()
        case "Qadim_The_Peerless":
            return QadimThePeerlessParser()
        case "Samarog":
            return SamarogParser()
    print("Factory didnt find a Parser for boss", boss)