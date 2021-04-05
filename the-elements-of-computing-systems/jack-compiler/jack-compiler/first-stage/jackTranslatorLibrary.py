# An intermediate code library for the Jack > Intermediate code translation. @DimitarYordanov17

class JackTranslatorLibrary:
    """
    Main class to map the Jack language to intermediate (VM) code
    """

    def _parse_comment(line, comment):
	    """
	    Returns a string, which is parsed from the line and a boolean, which signals if we are entering a block comment
	    """
	
	    line = line.rstrip()
	    comment_occurrences = [occurence.span()[0] for occurence in re.finditer(comment, line)]
	    
	    string_to_write = line + '\n'
	    enter_block_comment = False
	    
	    for comment_start_index in comment_occurrences:
	        before_comment_segment = line[:comment_start_index]
	        double_quotes_count = before_comment_segment.count('"')
	        
	        if double_quotes_count % 2 == 0: # We have a comment, because all possible string are closed
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
	                string_to_write, enter_comment = _parse_comment(line, comment)
	                
	                in_comment = enter_comment
	
	                if string_to_write != '\n' and string_to_write != '':
	                    input_file.write(string_to_write)
	
	            elif (len(line.strip()) >= 2) and ("*/" == (line.strip()[-2] + line.strip()[-1])):
	                in_comment = False
	
	            elif (not in_comment) and line != '\n':
	                input_file.write(line)
	
	        input_file.truncate()
	
	    return 0