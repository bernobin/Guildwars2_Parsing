class ParserUI:
    def __init__(self):
        self.registered_parsers = set()

    def create_parser(self):
        parsers = []

        for index, parser in enumerate(self.registered_parsers):
            parsers.append(parser)
            print(f'{index} {parser.boss : <20} {len(list(parser.log_directory.glob("*.zevtc"))) : >4} files')

        selected_index = int(input("select the index of one boss:\n"))
        if selected_index in range(len(self.registered_parsers)):
            return parsers[selected_index]
        else:
            raise ValueError("input must be between 0 and", len(parsers)-1)
