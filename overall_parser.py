import result_parser
import race_parser

def parse_results(raw_data):
    header_lines = result_parser.get_header(raw_data)
    field_defs = result_parser.get_field_defs(header_lines)
    result_lines = result_parser.filter_to_result_lines(header_lines, raw_data, False)
    mapped_results = result_parser.get_mapped_results(field_defs, result_lines)
    mapped_results = result_parser.normalize(mapped_results)
    race_info = race_parser.get_race_info(result_parser.filter_to_result_lines(header_lines, raw_data, True))
    
    return {"race_info": race_info, "results": mapped_results}
    