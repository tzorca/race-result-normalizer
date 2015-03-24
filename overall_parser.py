import result_parser
import race_parser

def parse_multiple_results_files(filename_list):
    race_id = 1
    multiple_file_parse = {"race_info": [], "results": []}
    
    for filename in filename_list:
        if not filename.endswith(".txt"):
            continue
        
        file_parse = parse_results_file(filename, race_id)
        multiple_file_parse["race_info"].append(file_parse["race_info"])
        multiple_file_parse["results"].extend(file_parse["results"])
        race_id += 1
    
    return multiple_file_parse

def parse_results_file(filename, race_id):
    with open(filename, "r") as input_file:
        data_from_file = input_file.read()
    header_lines = result_parser.get_header(data_from_file)
    
    if (header_lines is None):
        print("Could not read header in " + filename)
        return
        
    
    field_defs = result_parser.get_field_defs(header_lines)
    result_lines = result_parser.filter_to_result_lines(header_lines, data_from_file, False)
    mapped_results = result_parser.get_mapped_results(field_defs, result_lines)
    mapped_results = result_parser.normalize(mapped_results)
    add_to_each_row(mapped_results, {"race_id":race_id})
    race_info = race_parser.get_race_info(result_parser.filter_to_result_lines(header_lines, data_from_file, True))
    race_info['id'] = race_id
    
    return {"race_info": race_info, "results": mapped_results}
    
def add_to_each_row(dictionary_list, extra):
    for row in dictionary_list:
        row.update(extra)
    