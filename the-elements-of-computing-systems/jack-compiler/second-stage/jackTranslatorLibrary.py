# An intermediate code library for the Jack > Intermediate code translation. @DimitarYordanov17

# TODO: Implement rest statement and term translations, might check tests
# TODO: Implement object (class initializations) and array handling - check _translate_object_initalization method, more info there
# TODO: Test expression list translation

import re
import copy

class JackTranslatorLibrary:
    """
    A main library class capable of Jack language syntax analysis and VM code generation
    """


    SYNTAX_ELEMENTS = {

        "symbols": ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'],

        "subroutines": ['constructor', 'function', 'method'],
        
        "primitive_types": ['var', 'static', 'field'],

        "statements": ['let', 'if', 'while', 'do', 'return'],

        "op": ['+', '-', '*', '/', '&', '~', '|', '<', '>', '='],

        "keywords": ['class', 'constructor', 'function',
                     'method', 'field', 'static', 'var',
                     'int', 'char', 'boolean', 'void', 'true',
                     'false', 'null', 'this', 'let', 'do',
                     'if', 'else', 'while', 'return'],
    }

    def translate_file(input_file_name):
        """
        Handle the translation of a file
        """
                
        jack_translator = JackTranslatorLibraryCodeGenerator(input_file_name)
        vm_code = jack_translator.translate()

        return vm_code


    def parse_file(input_file_name):
        """
        Makes use of the JackTranslatorLibraryParser class to generate a .xml file from a .jack one
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

            # Clean spaces, without breaking the string
            # BTW I spent too much time on this but in the end I see that
            # I could use regex techniques for the entire compiler...
            # If I find time to rework the whole thing, I might find a way
            # to do it with regexes for optimization.
            # All the added complexity is here just so I can parse strings the correct way.

            strings = re.findall(r'"[^"]*"', file_text)
            non_string_file_text = re.split(r'(?:"[^"]*")', file_text)

            refactored_text = []

            for index, non_string in enumerate(non_string_file_text):
                while "  " in non_string:
                    non_string = non_string.replace("  ", " ")

                for symbol in JackTranslatorLibrary.SYNTAX_ELEMENTS["symbols"]:
                    widened_symbol = " " + symbol + " "
                    non_string = non_string.replace(symbol, widened_symbol)

                refactored_text.extend(non_string.split())

                try:
                    refactored_text.append(strings[index])
                except:
                    break

            input_file.seek(0)

            for token in refactored_text:
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


class JackTranslatorLibraryCodeGenerator:
    """
    Responsible for the VM code generation of Jack commands and other auxiliary functions (such as building symbolic table)
    XML -> VM.
    
    More information on the translating logic:
    // We have a basic initialization where each instance contains input_commands (all the XML tags) and
    // subroutines (a dictionary - subroutine_name: [subroutine_declaration, subroutine_symbolic_table, vm_code]).
    // Next, we translate all the class information (class variables...). After that we go through every
    // subroutine and we translate it to VM code, using its own symbolic table. To translate the file means
    // to fill up instance's vm_code attribute
    """
    OPERATIONS = {  "+": "add", "-": "sub", "&": "and", "|": "or",
                    "*": "call Math.multiply()", "/": "call Math.divide()",
                    ">": "gt", "<": "lt", "=": "eq"
                }

    def __init__(self, input_file_name):
        self.input_commands = open(input_file_name, 'r').readlines()
        self.symbolic_table = []
        self.vm_code = []

        self.subroutines = {}
        self.class_info = []

    def translate(self):
        """
        Get class and subroutines info. Generate symbolic table for every subroutine. Start parsing every subroutine
        """
        
        JackTranslatorLibraryCodeGenerator._strip_input_commands(self)
        JackTranslatorLibraryCodeGenerator._get_class_info(self)        
        JackTranslatorLibraryCodeGenerator._get_subroutines(self)

        for subroutine_name in self.subroutines.keys():
            symbolic_table = JackTranslatorLibraryCodeGenerator._generate_symbolic_table(self, subroutine_name)
            self.subroutines[subroutine_name].append(symbolic_table)
        
        for subroutine_name in self.subroutines.keys():
            subroutine_vm_code = JackTranslatorLibraryCodeGenerator._translate_subroutine(self, subroutine_name)
            self.subroutines[subroutine_name].append(subroutine_vm_code)

        vm_code = []

        for subroutine_declaration, subroutine_symbolic_table, subroutine_vm_code in self.subroutines.values():
            indented_vm_code = [vm_command + '\n' for vm_command in subroutine_vm_code]
            vm_code.extend(indented_vm_code)

        return vm_code

        # \/ Print subroutines for testing \/
        #for subroutine_name, properties in self.subroutines.items():
        #    print(f"{subroutine_name}:\n{properties[1]}\n{properties[2]}\n")

    def _translate_subroutine(self, subroutine_name):
        """
        Return the vm code for a subroutine
        """
        
        subroutine_declaration = self.subroutines[subroutine_name][0]
        subroutine_symbolic_table = self.subroutines[subroutine_name][1]
        class_name = self.class_info[0]

        subroutine_vm_code = []

        # Translate meta information
        subroutine_title = f"function {class_name}.{subroutine_name}"
        subroutine_kind = JackTranslatorLibraryParser._get_tag_value(self, subroutine_declaration[0])
        arguments_count = [x for y in list(subroutine_symbolic_table.values()) for x in y].count("argument")

        subroutine_declaration_title = subroutine_title + f" {arguments_count}"
        subroutine_vm_code.append(subroutine_declaration_title)

        # Add translation bootstrap code (setting the "this" segment)
        if subroutine_kind == "method":
            subroutine_vm_code.extend(["push argument 0", "pop pointer 0"])
        
        elif subroutine_kind == "constructor":
            class_variables = [x for y in list(self.class_info[1].values()) for x in y].count("field")
            subroutine_vm_code.extend([f"push constant {class_variables}", "call Memory.alloc", "pop pointer 0"])

        subroutine_body = subroutine_declaration[subroutine_declaration.index("<statements>"):JackTranslatorLibraryCodeGenerator._get_all_occurrences(subroutine_declaration, "</statements>")[-1]] 
        statements_vm_code = JackTranslatorLibraryCodeGenerator._translate_statements(self, subroutine_body, subroutine_name)
        subroutine_vm_code.extend(statements_vm_code)

        return subroutine_vm_code


    def _translate_statements(self, statement_declarations, subroutine_name):
        """
        Return the vm code for every statement in a subroutine body
        """

        statements_vm_code = []

        statements = []
        current_statement = []
        statement_stack = []

        # Differentiate all statements (not recursively!)
        for tag in statement_declarations[1:-1]:
            current_statement.append(tag)
            if "Statement" in tag and "/" not in tag:
                statement_stack.append(tag)

            elif "Statement" in tag and "/" in tag:
                if len(statement_stack) == 1:
                    statements.append(current_statement)
                    current_statement = []
                statement_stack.pop()

        # Translate the differentiated statements
        for statement_declaration in statements:
            statement_type = statement_declaration[0][1:-1]
            statement_vm_code = []

            if statement_type == "letStatement":
                # Get identifier notation
                identifier = JackTranslatorLibraryParser._get_tag_value(self, statement_declaration[2])
                identifier = JackTranslatorLibraryCodeGenerator._get_identifier(self, identifier, subroutine_name)

                # Get expression declaration
                expression_declaration = statement_declaration[statement_declaration.index("<symbol> = </symbol>") + 2:-3]

                # Check if we have a object initialization
                initializing_object = JackTranslatorLibraryParser._get_tag_value(self, expression_declaration[0]) == "new"

                # Translate expression or object initalization
                if initializing_object:
                    expression_vm_code = JackTranslatorLibraryCodeGenerator._translate_object_initialization(self, expression,_declaration, subroutine_name)
                else:
                    expression_vm_code = JackTranslatorLibraryCodeGenerator._translate_expression(self, expression_declaration, subroutine_name)

                # Check if we our identifier is an array
                array_indexing = JackTranslatorLibraryParser._get_tag_value(self, statement_declaration[3]) == "["

                # Construct statement code
                if array_indexing:
                    identifier_expression_declaration  = statement_declaration[5:statement_declaration.index("</expression>")]
                    identifier_vm_code = JackTranslatorLibraryCodeGenerator._translate_expression(self, identifier_expression_declaration, subroutine_name)

                    # Calculate identifier address
                    statement_vm_code.extend([f"push {identifier}"])
                    statement_vm_code.extend(identifier_vm_code)
                    statement_vm_code.append("add")

                    # Pop into that
                    statement_vm_code.append("pop pointer 1")

                    # Push expression value
                    statement_vm_code.extend(expression_vm_code)

                    # Pop into the desired address
                    statement_vm_code.append("pop that 0")

                else:
                    # Push expression value
                    statement_vm_code.extend(expression_vm_code)

                    # Pop into the desired segment
                    statement_vm_code.append(f"pop {identifier}")
                

            elif statement_type == "ifStatement":
                # Translate if statement
                pass

            elif statement_type == "whileStatement":
                # Translate while statement
                pass

            elif statement_type == "doStatement":
                # ...
                pass

            elif statement_type == "ReturnStatement":
                # ...
                pass

            statements_vm_code.extend(statement_vm_code)

        return statements_vm_code

    # ~~~~~~~~~~~~~~~~~~~~~~~~ Fundamental translation ~~~~~~~~~~~~~~~~~~~~~~~~
    def _translate_object_initialization(self, expression_declaration, subroutine_name):
        """
        Get the vm code for object init
        """

        object_initialization_vm_code = []

        # TODO: Write logic

        return object_initialization_vm_code

    def _translate_expression(self, expression_declaration, subroutine_name):
        """
        Translate a sequence of terms to VM code.
        """

        expression_vm_code = []

        # Terms and operations will keep differentiated structures
        terms = []
        operations = []

        # Differentiate into terms and operations
        current_term = []
        stack = []

        for index, tag in enumerate(expression_declaration):
            
            if "term" in tag and " " not in tag:
                if "/" in tag:
                    stack.pop()
                else:
                    stack.append(1)
            
            if len(stack) > 0:
                current_term.append(tag)
            else:
                tag_value = JackTranslatorLibraryParser._get_tag_value(self, tag)
                if tag_value in JackTranslatorLibrary.SYNTAX_ELEMENTS["op"]:
                    operations.append(tag_value)
                else:
                    terms.append(current_term[1:])
                    current_term = []

        # Translate each term
        terms_vm = []
        for term in terms:
            terms_vm.append(JackTranslatorLibraryCodeGenerator._translate_term(self, term, subroutine_name))

        # Construct expression VM code
        expression_vm_code.extend(terms_vm[0])

        if len(terms_vm) > 1:
            expression_vm_code.extend(terms_vm[1])

            for index, operation in enumerate(operations):
                operation_vm = JackTranslatorLibraryCodeGenerator.OPERATIONS[operation]

                expression_vm_code.append(operation_vm)

                try:
                    expression_vm_code.extend(terms_vm[index + 2])
                except:
                    break

        return expression_vm_code


    def _translate_term(self, term_declaration, subroutine_name):
        """
        Translate a term to VM code
        """
        term_vm_code = []

        if len(term_declaration) == 1: # Single identifier/constant
            term_type = term_declaration[0].split()[0][1:-1]
            term_value = JackTranslatorLibraryParser._get_tag_value(self, term_declaration[0])

            print(term_value, term_type)

            if term_type == "identifier":
                term_vm_code.append(f"push {JackTranslatorLibraryCodeGenerator._get_identifier(self, term_value, subroutine_name)}")
            else:
                term_vm_code.append(f"push {term_value}")

        else:
            term_value = JackTranslatorLibraryParser._get_tag_value(self, term_declaration[0])
            next_token = JackTranslatorLibraryParser._get_tag_value(self, term_declaration[1])
            if  next_token in [".", "("]: # Subroutine call
                if next_token == ".": # Method call
                    term_vm_code.append("push this")

                expression_list = term_declaration[term_declaration.index("<symbol> ( </symbol>") + 2: -2]
                expression_list_vm_code = JackTranslatorLibraryCodeGenerator._translate_expression_list(self, expression_list, subroutine_name)

                for vm_command in expression_list_vm_code:
                    term_vm_code.extend(vm_command)

                if next_token == ".":
                    term_vm_code.append(f"call {term_value}.{JackTranslatorLibraryParser._get_tag_value(self, term_declaration[2])}")
                else:
                    term_vm_code.append(f"call {JackTranslatorLibraryParser._get_tag_value(self, term_declaration[0])}")

            elif next_token == "[": # varName indexing
                array_indexing_expression = term_declaration[term_declaration.index("<symbol> [ </symbol>") + 2: -2]
                array_indexing_expression_vm_code = JackTranslatorLibraryCodeGenerator._translate_expression(self, array_indexing_expression, subroutine_name)

                identifier = JackTranslatorLibraryCodeGenerator._get_identifier(self, term_value, subroutine_name)

                term_vm_code.extend([f"push {identifier}"])
                term_vm_code.extend(array_indexing_expression_vm_code)
                term_vm_code.append("add")

                term_vm_code.append("pop pointer 1")

                term_vm_code.append("push that 0")

            elif term_value in JackTranslatorLibrary.SYNTAX_ELEMENTS["op"]: # unaryOp term
                term_expression = term_declaration[1:]
                
                term_expression_vm_code = JackTranslatorLibraryCodeGenerator._translate_expression(self, term_expression, subroutine_name)

                term_vm_code.extend(term_expression_vm_code)

                command_expression = "neg" if term_value == "-" else "not"

                term_vm_code.append(command_expression)

            elif term_value == "(": # Bracket expression
                term_expression = term_declaration[2:-2]
                term_expression_vm_code = JackTranslatorLibraryCodeGenerator._translate_expression(self, term_expression, subroutine_name)

                term_vm_code.extend(term_expression_vm_code)

        return term_vm_code

    def _translate_expression_list(self, expression_list_declaration, subroutine_name):
        """
        Translate a sequence of expressions to VM code.
        /* WARNNING: Method not tested*/
        """

        expression_list_vm_code = []

        # expressions will contain every separate expression
        expressions = []

        # Differentiate into expressions and operations
        current_expression = []
        stack = []

        for index, tag in enumerate(expression_list_declaration):
            tag_value = JackTranslatorLibraryParser._get_tag_value(self, tag)

            if " " not in tag and "expression" in tag:
                if "/" in tag:
                    stack.pop()
                else:
                    stack.append(1)

                if len(stack) == 0:
                    expressions.append(current_expression)
                    current_expression = []
                    continue

            elif tag_value != ",":
                current_expression.append(tag)

        # Extend the expression list VM code with which individual expression VM code

        for expression in expressions:
            expression_list_vm_code.append(JackTranslatorLibraryCodeGenerator._translate_expression(self, expression, subroutine_name))

        return expression_list_vm_code

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~ Auxiliary translation ~~~~~~~~~~~~~~~~~~~~~~~
    def _get_identifier(self, identifier, subroutine_name):
        """
        Return the correct identifier properties, handle scoping
        """

        try: # Search for the identifier declaration in current scope
            identifier = self.subroutines[subroutine_name][1][identifier]
        except KeyError: # Search in global scope
            identifier = self.class_info[1][identifier]
        
        identifier_type, identifier_kind, identifier_count = identifier[0], identifier[1], identifier[2]
        identifier_segment = identifier_kind
        
        if identifier_kind == "var":
            identifier_segment = "local"
        elif identifier_kind == "field":
            identifier_segment = "this"

        identifier_vm = f"{identifier_segment} {identifier_count}"
        
        return identifier_vm

    def _get_subroutines(self):
        """
        Find all name and declaration for subroutines and add them to self.subroutines
        """
        
        subroutine_declarations = JackTranslatorLibraryCodeGenerator._get_tag_body(self, "<subroutineDec>")

        for subroutine_declaration in subroutine_declarations:
            subroutine_name = JackTranslatorLibraryParser._get_tag_value(self, subroutine_declaration[2])

            self.subroutines[subroutine_name] = [subroutine_declaration]


    def _get_class_info(self):
        """
        Get class name and generate class symbolic table, which are going to be used in translation later
        """

        class_name = JackTranslatorLibraryParser._get_tag_value(self, self.input_commands[2])
        
        class_symbolic_table = {}

        variable_declarations = JackTranslatorLibraryCodeGenerator._get_tag_body(self, "<classVarDec>")

        count = 0
        last_kind = ""

        for variable_declaration in variable_declarations:
            variable_declaration = [JackTranslatorLibraryParser._get_tag_value(self, tag) for tag in variable_declaration]

            variable_kind = variable_declaration[0]

            if variable_kind != last_kind:
                count = 0

            variable_type = variable_declaration[1]

            variable_names = [name for name in variable_declaration[2:] if name != ',']

            for variable_name in variable_names:
                class_symbolic_table[variable_name] = [variable_type, variable_kind, count]
                count += 1

            last_kind = variable_kind
            

        self.class_info = [class_name, class_symbolic_table]


    def _get_tag_body(self, tag, gap=1, field_to_search="input_commands"):
        """
        /* WARNING: Do not use this when there are possible nested structures, e.g. expression parsing */
        Return all the statements (tags) between an opening and closing tag (the argument) in a given field (the default being self.input_commands), for every tag combination.
        Gap is used for the cleaning of e.g. statement ending semicolons
        """

        if field_to_search == "input_commands":
            field_to_search = self.input_commands

        starting_indices = JackTranslatorLibraryCodeGenerator._get_all_occurrences(field_to_search, tag)
        ending_indices = JackTranslatorLibraryCodeGenerator._get_all_occurrences(field_to_search, JackTranslatorLibraryParser._get_closed_tag(self, tag))

        declarations = []

        for starting_index, ending_index in zip(starting_indices, ending_indices):
            declaration = field_to_search[starting_index + 1: ending_index - gap] 
            declarations.append(declaration)

        return declarations


    def _generate_symbolic_table(self, subroutine_name):
        """
        Build up symbolic table for subroutine delcarations to handle identifiers type and scope problems
        """

        subroutine_declaration = self.subroutines[subroutine_name][0]
        symbolic_table = dict()

        # Parse arguments variables
        parameter_list = JackTranslatorLibraryCodeGenerator._get_tag_body(self, "<parameterList>", gap=0, field_to_search=subroutine_declaration)

        subroutine_type = JackTranslatorLibraryParser._get_tag_value(self, subroutine_declaration[0])

        if subroutine_type == "method":
            subroutine_kind = JackTranslatorLibraryParser._get_tag_value(self, subroutine_declaration[1])
            symbolic_table["this"] = [self.class_info[0], "argument", 0]

        if parameter_list:
            parameter_list = parameter_list[0] # There is only one parameterList tags pair

            parameter_variables = list(filter(lambda symbol: symbol != "<symbol> , </symbol>", parameter_list))

            parameter_variables = [[parameter_variables[index], parameter_variables[index + 1]] for index in range(0, len(parameter_variables), 2)]
            # /\ Transforms [type, identifier, ',', type, identifier...] into [[type, identifier], [type, identifier]...] /\

            for count, var_pair in enumerate(parameter_variables):
                if subroutine_type == "method":
                    count += 1

                var_type, var_name = var_pair[0], var_pair[1]
                symbolic_table[JackTranslatorLibraryParser._get_tag_value(self, var_name)] = [JackTranslatorLibraryParser._get_tag_value(self, var_type), "argument", count]


        # Subroutine body variables
        variable_declarations = JackTranslatorLibraryCodeGenerator._get_tag_body(self, "<varDec>", field_to_search=subroutine_declaration)

        count = 0

        for variable_declaration in variable_declarations:
            variable_declaration = [JackTranslatorLibraryParser._get_tag_value(self, tag) for tag in variable_declaration]

            variable_type = variable_declaration[1]
            variable_kind = variable_declaration[0]

            variable_names = [name for name in variable_declaration[2:] if name != ',']

            for variable_name in variable_names:
                symbolic_table[variable_name] = [variable_type, variable_kind, count]
                count += 1

        return symbolic_table

    def _strip_input_commands(self):
        """
        Remove every \n for easier work
        """

        for index, line in enumerate(self.input_commands):
            self.input_commands[index] = line.rstrip()

    def _get_all_occurrences(elements_list, element):
        """
        Return all occurrences of a given element in elements_list
        """
        
        index_list = []
        index_position = 0

        while True:
            try:
                index_position = elements_list.index(element, index_position)
                index_list.append(index_position)
                index_position += 1
            except ValueError as e:
                break

        return index_list


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
            token_value = JackTranslatorLibraryParser._get_tag_value(self, token)

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
            token_value = JackTranslatorLibraryParser._get_tag_value(self, token)

            if token_value == "(":
                if JackTranslatorLibraryParser._get_tag_value(self, subroutine_tokens[index + 1]) == ")":
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

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])
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

            current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])
            current_token_full = self.tokens[self.row_pointer]

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1

    # ~~~~~~~~~~~~~~ General statement parsing ~~~~~~~~~~~~~~~~~

    def _parse_let(self):
        """
        Node of _parse_statements
        """

        self.row_pointer += 2

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

        if current_token == "=":
            if JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer + 1]) == "new":
                self.row_pointer += 1

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

        next_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer + 1])

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

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

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

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

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

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

        while current_token in JackTranslatorLibrary.SYNTAX_ELEMENTS["op"]:
            self.row_pointer += 1

            JackTranslatorLibraryParser._parse_term(self)
            current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1


    def _parse_expression_list(self):
        """
        Node of _parse_let;do;if;while;return
        """
        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

        if current_token == ")":
            return

        tag = "<expressionList>\n"

        self.tokens.insert(self.row_pointer, tag)
        self.row_pointer += 1

        JackTranslatorLibraryParser._parse_expression(self)

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

        while current_token == ",":
            self.row_pointer += 1

            JackTranslatorLibraryParser._parse_expression(self)
            current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])

        self.tokens.insert(self.row_pointer, JackTranslatorLibraryParser._get_closed_tag(self, tag))
        self.row_pointer += 1


    def _parse_term(self):
        """
        Node of _parse_expression
        """

        tag = "<term>\n"

        current_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer])
        current_token_type = self.tokens[self.row_pointer].split(" ")[0][1:-1]

        next_token = JackTranslatorLibraryParser._get_tag_value(self, self.tokens[self.row_pointer + 1])

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


    def _get_tag_value(self, tag):
        """
        Returns mediocre keyword
        """
        try:
            return tag.split()[1]
        except:
            return tag
