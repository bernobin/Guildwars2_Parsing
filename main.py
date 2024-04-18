from PARSING.Parser_Factory import ParserUI
from PARSING.Cerus_Parser import CerusParser
from PARSING.QadimThePeerless_Parser import QadimThePeerlessParser
from PARSING.Qadim_Parser import QadimParser
from PARSING.Samarog_Parser import SamarogParser
from PARSING.Gorseval_Parser import GorsevalParser

from PARSING.Cerus_Parser_Timeline import CerusParserTimeline

###
### Automate token deletion if expired
### MOVE nan replacer into class method for create googlesheet
###


def main():
    # should be a singleton
    parser_ui = ParserUI()

    cerus_parser = CerusParser()
    cerus_parser.subscribe_to_ui('cerus', parser_ui)

    qadimp_parser = QadimThePeerlessParser()
    qadimp_parser.subscribe_to_ui('qadim the peerless', parser_ui)

    qadim_parser = QadimParser()
    qadim_parser.subscribe_to_ui('qadim', parser_ui)

    sama_parser = SamarogParser()
    sama_parser.subscribe_to_ui('samarog', parser_ui)

    gorse_parser = GorsevalParser()
    gorse_parser.subscribe_to_ui('gorseval', parser_ui)

    cerus_parser_timeline = CerusParserTimeline()
    cerus_parser_timeline.subscribe_to_ui('cerus timeline', parser_ui)

    parser = parser_ui.create_parser()
#    parser.get_csv()
    parser.get_googlesheet(sheet_id='1X_o-88KodsNycnV2FfX0egNkdqjUkQsdjvoXpfIRZO0')


if __name__ == '__main__':
    main()
