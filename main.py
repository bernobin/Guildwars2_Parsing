from PARSING.Parser_Factory import ParserUI
from PARSING.Cerus_Parser import CerusParser
from PARSING.QadimThePeerless_Parser import QadimThePeerlessParser
from PARSING.Qadim_Parser import QadimParser
from PARSING.Samarog_Parser import SamarogParser
from PARSING.Gorseval_Parser import GorsevalParser


###
### Automate token deletion if expired
###

def main():
    # should be a singleton
    pui = ParserUI()

    cerus_parser = CerusParser()
    cerus_parser.subscribe_to_ui(pui)

    qadimp_parser = QadimThePeerlessParser()
    qadimp_parser.subscribe_to_ui(pui)

    qadim_parser = QadimParser()
    qadim_parser.subscribe_to_ui(pui)

    sama_parser = SamarogParser()
    sama_parser.subscribe_to_ui(pui)

    gorse_parser = GorsevalParser()
    gorse_parser.subscribe_to_ui(pui)

    parser = pui.create_parser()
    parser.get_googlesheet(sheet_id='1X_o-88KodsNycnV2FfX0egNkdqjUkQsdjvoXpfIRZO0')


if __name__ == '__main__':
    main()
