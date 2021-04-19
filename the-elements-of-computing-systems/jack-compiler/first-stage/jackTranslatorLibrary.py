# An intermediate code library for the Jack > Intermediate code translation. @DimitarYordanov17
# (This is a first-stage library - only Jack -> XML proccessing, tokenizng, cleaning and tabularizing)
# (More info about the parsing logic at line 197)

import re

class JackTranslatorLibrary:
    """
    A main library class capable of Jack language syntax analysis
    """


    SYNTAX_ELEMENTS = {

        "symbols": ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'],

        "subroutines": ['constructor', 'function', 'method'],

        "statements": ['let', 'if', 'while', 'do', 'return'],

        "op": ['+', '-', '*', '/', '&', '|', '<', '>', '='],

        "keywords": ['class', 'constructor', 'function',
                     'method', 'field', 'static', 'var',
                     'int', 'char', 'boolean', 'void', 'true',
                     'false', 'null', 'this', 'let', 'do',
                     'if', 'else', 'while', 'return'],
    }


    def parse_file(input_file_name):
        """
        Makes use of the JackTranslatorLibraryParser class to construct a .xml file from a .jack one
        """

        jack_parser = JackTranslatorLibraryParser(input_file_name)
        jack_parser.parse()


    def tokenize(input_file_name):
        """
        Tokenizes a file, spreading each keyword (token) on a newline
        """

        with open(input_file_name, 'r+') as input_file:
            input_file.seek(0)
            file_text = input_file.read()

            # Clean trailing spaces
            file_text = file_text.strip()

            # Clean all \n
            file_text = file_text.replace("\n", " ")

            # Wider all symbols
            for symbol in JackTranslatorLibrary.SYNTAX_ELEMENTS["symbols"]:
                widened_symbol = " " + symbol + " "
                file_text = file_text.replace(symbol, widened_symbol)

            # Clean all in-file spaces
            while "  " in file_text:
                file_text = file_text.replace("  ", " ")

            # Split into tokens
            file_text = file_text.split()

            input_file.seek(0)

            for token in file_text:
                classified_token = JackTranslatorLibrary._classify_token(token)
                input_file.write(classified_token + '\n')

            input_file.truncate()


    def clean(input_file_name):
        """
        Removes all comments in a file, but keeps line spacing
        (have to be careful to not remove a line which contains
        division, signed by '/' or string, containing it)
        """

        with open(input_file_name, 'r+') as input_file:
            lines = input_file.readlines()
            input_file.seek(0)

            in_comment = False

            for line in lines:
                if "/*" in line or "//" in line:
                    comment = r"//" if "//" in line else r"/\*"
                    string_to_write, enter_comment = JackTranslatorLibrary._proccess_comment(line, comment)

                    in_comment = enter_comment

                    if string_to_write != '\n' and string_to_write != '':
                        input_file.write(string_to_write)

                elif (len(line.strip()) >= 2) and ("*/" == (line.strip()[-2] + line.strip()[-1])):
                    in_comment = False

                elif (not in_comment) and line != '\n':
                    input_file.write(line)

            input_file.truncate()


    def tabularize(input_file_name):
        """
        Indent every tag between two upper tags, keep nested depth
        """

        with open(input_file_name, 'r+') as input_file:
            lines = input_file.readlines()
            input_file.seek(0)

            depth = 0

            for line in lines:
                tabularized_line = ('\t' * depth) + line

                if " " not in line:
                    if "/" in line:
                        depth -= 1
                        tabularized_line = ('\t' * depth) + line
                    else:
                        depth += 1

                input_file.write(tabularized_line)


    def _classify_token(token):
        """
        Appends a certain type tags to a token 
        """

        token_type = ""

        if token in JackTranslatorLibrary.SYNTAX_ELEMENTS["keywords"]:
            token_type = "keyword"

        elif token in JackTranslatorLibrary.SYNTAX_ELEMENTS["symbols"]:
            token_type = "symbol"

        elif '"' in token_type:
            token_type = "StringConstant"

        elif token[0].isnumeric():
            token_type = "integerConstant"

        else:
            token_type = "identifier"

        classified_token = f"<{token_type}> {token} </{token_type}>"

        return classified_token


    def _proccess_comment(line, comment):
        """
        Returns a string, that should be written and a boolan to indicate if we are entering a block comment
        """

        line = line.rstrip()
        comment_occurrences = [occurence.span()[0] for occurence in re.finditer(comment, line)]

        string_to_write = line + '\n'
        enter_block_comment = False

        for comment_start_index in comment_occurrences:
            before_comment_segment = line[:comment_start_index]
            double_quotes_count = before_comment_segment.count('"')

            if double_quotes_count % 2 == 0:  # We have a comment, because all possible string are closed
                if before_comment_segment.replace(" ", ""):
                    string_to_write = before_comment_segment + '\n'

                else:
                    string_to_write = ""

                if "/*" in line:
                    last_two_chars = line[-2] + line[-1]
                    enter_block_comment = True

                    if last_two_chars == "*/":
                        enter_block_comment = False

                break

        return string_to_write, enter_block_comment


class JackTranslatorLibraryParser:
    """
    Parse a cleaned, tokenized and classified file (Jack) and return the corresponding XML code

    More information on the parsing logic:
    // We start with the initializing of the class - make an instance, containing tokens (classified Jack keywords) and a row_pointer (used to
    // indicate the current working index).Then we are parsing a file - call a parsing function (in this case _parse_class()) and then write the
    // modified tokens to the file. The work of the _parse_class() function on the other side is pretty interesting - we start calling another
    // inner functions, which call another inner functions. The whole proccess of parsing a file is sequential
    // with recursive elements (e.g. expression parsing).
    """

    def __init__(self, input_file_name):
        self.input_file_name = input_file_name
        self.input_file = open(input_file_name, 'r')
        self.tokens = self.input_file.readlines()

        self.row_pointer = 0

    def parse(self):
        """
        Parse a single file
        """

        JackTranslatorLibraryParser._parse_class(self)

        with open(self.input_file_name, 'w') as input_file:
            input_file.seek(0)

            for line in self.tokens:
                input_file.write(line)

            input_file.truncate()

    # ~~~~~~~~~~~~~ File parsing nodes ~~~~~~~~~~~~~~~~~~~~~~~~~

    def _parse_class(self):
        """
        Parse a class (actually file parsing, but we know that there is only a single class in a file)
        """

        tag = "<class>\n"

        self.tokens.insert(self.row_pointer, tag)
        self.tokens.insert(len(self.tokens), JackTranslatorLibraryParser._get_closed_tag(self, tag))

        self.row_pointer += 4

        JackTranslatorLibraryParser._parse_variableDeclarations(self, class_vars=True)
        JackTranslatorLibraryParser._parse_subroutineDeclarations(self)


    def _parse_variableDeclarations(self, class_vars=False):
        """
        Node of _parse_class
        """

        tag = "<classVarDec>\n" if class_vars else "<varDec>\n"
        body = self.tokens[self.row_pointer:]

        for token in body:
            token_value = JackTranslatorLibraryParser._get_token_value(self, token)

            if token_value == "var" or token_value == "static" or token_value == "field":
                self.tokens.insert(self.row_pointer, tag)
                self.row_pointer += 1

            if token_value == ";":
                self.tokens.insert(self.row_pointer + 1, JackTranslatorLibraryParser._get_closed_tag(self, tag))
                self.row_pointer += 1

            self.row_pointer += 1

            if class_vars:
                if token_value in JackTranslatorLibrary.SYNTAX_ELEMENTS["subroutines"]:
                    self.row_pointer -= 1
                    break
            else:
                if token_value in JackTranslatorLibrary.SYNTAX_ELEMENTS["statements"]:
                    self.row_pointer -= 1
                    break


    def _parse_subroutineDeclarations(self):
        """
        Node of _parse_class
        """

        current_token = self.tokens[self.row_pointer]

        while current_token != "</class>\n" and current_token != "<symbol> } </symbol>\n":
            JackTranslatorLibraryParser._parse_subroutineDeclaration(self)
            current_token = self.tokens[self.row_pointer]


    def _parse_subroutineDeclaration(self):
        """
        Node of _parse_subroutineDeclarations
        """

        dec_tag = "<subroutineDec>\n"
        param_list_tag = "<parameterList>\n"

        self.tokens.insert(self.row_pointer, dec_tag)
        self.row_pointer += 1

        subroutine_tokens = self.tokens[self.row_pointer:]

        for index, token in enumerate(subroutine_tokens):
            token_value = JackTranslatorLibraryParser._get_token_value(self, token)

            if token_value == "(":
                if JackTranslatorLibraryParser._get_token_value(self, subroutine_tokens[index + 1]) == ")":
                    self.row_pointer += 3
                    break
                else:
                    self.row_pointer += 1
                    self.tokens.insert(self.row_pointer, param_list_tag)
            elif token_value == ")":
                self.tokens.insert(self.row_pointer,
                                   JackTranslatorLibraryParser._get_closed_tag(self, param_list_tag))
                self.row_pointer += 3
                break

            self.row_pointer += 1

        JackTranslatorLibraryParser._parse_subroutineBody(self)

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, dec_tag))
        self.row_pointer += 1


    def _parse_subroutineBody(self):
        """
        Node of _parse_subroutineDeclaration
        """

        tag = "<subroutineBody>\n"

        self.tokens.insert(self.row_pointer, tag)

        self.row_pointer += 1

        JackTranslatorLibraryParser._parse_variableDeclarations(self)

        JackTranslatorLibraryParser._parse_statements(self)

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1


    def _parse_statements(self, stop_value = "</subroutineDec>\n"):
        """
        Node of _parse_subroutineBody
        """

        tag = "<statements>\n"

        self.tokens.insert(self.row_pointer, tag)
        self.row_pointer += 1

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])
        current_token_full = self.tokens[self.row_pointer]

        while current_token_full != stop_value:
            statement_type = current_token + "Statement" if current_token != "return" else "ReturnStatement"
            statement_tag = f"<{statement_type}>\n"

            self.tokens.insert(self.row_pointer, statement_tag)
            self.row_pointer += 1

            if current_token == "let":
                JackTranslatorLibraryParser._parse_let(self)

            elif current_token == "do":
                JackTranslatorLibraryParser._parse_do(self)

            elif current_token == "if":
                JackTranslatorLibraryParser._parse_if(self)

            elif current_token == "while":
                JackTranslatorLibraryParser._parse_while(self)

            elif current_token == "return":
                JackTranslatorLibraryParser._parse_return(self)
                self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, statement_tag))
                self.row_pointer += 2
                break

            self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, statement_tag))
            self.row_pointer += 1

            current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])
            current_token_full = self.tokens[self.row_pointer]

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1

    # ~~~~~~~~~~~~~~ General statement parsing ~~~~~~~~~~~~~~~~~

    def _parse_let(self):
        """
        Node of _parse_statements
        """

        self.row_pointer += 2

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])

        if current_token == "=":
            self.row_pointer += 1
            JackTranslatorLibraryParser._parse_expression(self)
            self.row_pointer += 1

        else:
            self.row_pointer += 1
            JackTranslatorLibraryParser._parse_expression(self)
            self.row_pointer += 2

            JackTranslatorLibraryParser._parse_expression(self)
            self.row_pointer += 1


    def _parse_do(self):
        """
        Node of _parse_statements
        """

        self.row_pointer += 1

        next_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer + 1])

        if next_token == ".":  # Method call
            self.row_pointer += 4
        else:  # Function call
            self.row_pointer += 2

        JackTranslatorLibraryParser._parse_expression_list(self)

        self.row_pointer += 2


    def _parse_if(self):
        """
        Node of _parse_statements
        """

        self.row_pointer += 2

        JackTranslatorLibraryParser._parse_expression(self)

        self.row_pointer += 2

        JackTranslatorLibraryParser._parse_statements(self, stop_value="<symbol> } </symbol>\n")

        self.row_pointer += 1

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])

        if current_token == "else":
            self.row_pointer += 2

            JackTranslatorLibraryParser._parse_statements(self, stop_value="<symbol> } </symbol>\n")

            self.row_pointer += 1


    def _parse_while(self):
        """
        Node of _parse_statements
        """

        self.row_pointer += 2

        JackTranslatorLibraryParser._parse_expression(self)

        self.row_pointer += 2

        JackTranslatorLibraryParser._parse_statements(self, stop_value="<symbol> } </symbol>\n")

        self.row_pointer += 1


    def _parse_return(self):
        """
        Node of _parse_statements
        """

        self.row_pointer += 1

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])

        if current_token == ";":
            self.row_pointer += 1
            return

        JackTranslatorLibraryParser._parse_expression(self)
        self.row_pointer += 1
        
    # ~~~~~~~~~~~~ Statement auxiliary parsing ~~~~~~~~~~~~~~~~~

    def _parse_expression(self):
        """
        Node of _parse_expressionList
        """

        tag = "<expression>\n"

        self.tokens.insert(self.row_pointer, tag)
        self.row_pointer += 1

        JackTranslatorLibraryParser._parse_term(self)

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])

        if current_token in JackTranslatorLibrary.SYNTAX_ELEMENTS["op"]:
            self.row_pointer += 1
            JackTranslatorLibraryParser._parse_expression(self)

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1


    def _parse_expression_list(self):
        """
        Node of _parse_let;do;if;while;return
        """
        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])

        if current_token == ")":
            return

        tag = "<expressionList>\n"

        self.tokens.insert(self.row_pointer, tag)
        self.row_pointer += 1

        JackTranslatorLibraryParser._parse_expression(self)

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])

        if current_token == ",":
            self.row_pointer += 1
            JackTranslatorLibraryParser._parse_expression_list(self)

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1


    def _parse_term(self):
        """
        Node of _parse_expression
        """

        tag = "<term>\n"

        current_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer])
        current_token_type = self.tokens[self.row_pointer].split(" ")[0][1:-1]

        next_token = JackTranslatorLibraryParser._get_token_value(self, self.tokens[self.row_pointer + 1])

        self.tokens.insert(self.row_pointer, tag)
        self.row_pointer += 1

        if next_token == '[': # Array accessing
            self.row_pointer += 2

            JackTranslatorLibraryParser._parse_expression(self)
            self.row_pointer += 1

        elif current_token == "(": # Expression in brackets
            self.row_pointer += 1

            JackTranslatorLibraryParser._parse_expression(self)
            self.row_pointer += 1

        elif current_token == "-" or current_token == "~":  # Unary op
            self.row_pointer += 1
            JackTranslatorLibraryParser._parse_term(self)

        elif next_token == "(" or next_token == ".":  # Subroutine call
            if next_token == ".":  # Method call
                self.row_pointer += 4
            else:  # Function call
                self.row_pointer += 2

            JackTranslatorLibraryParser._parse_expression_list(self)
            self.row_pointer += 1

        else: # Single variable
            self.row_pointer += 1

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1

    # ~~~~~~~~~~~ Tag auxiliary ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_closed_tag(self, tag):
        """
        Appends '/' in the second place of the input
        """

        tag_list = list(tag)
        tag_list.insert(1, "/")
        return "".join(tag_list)


    def _get_token_value(self, tag):
        """
        Returns mediocre keyword
        """
        try:
            return tag.split()[1]
        except:
            return tag
