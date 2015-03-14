import os
import sys
import csv_processor
import result_parser

def main():
    if (len(sys.argv) < 2):
        script_name = os.path.basename(__file__)
        print ("Usage: " + script_name + " <filename>")
    else:
        filename = sys.argv[1]
        with open(filename, "r") as input_file:
            input_data = input_file.read()
        
        mapped_results = result_parser.parse_results(input_data)

        # For now, just outputs mapped results to tab-separated value list
        output_data = csv_processor.rows_to_csv(mapped_results, "\t")

        base_filename = os.path.splitext(filename)[0]
        with open(base_filename + ".tsv", "w") as output_file:
            output_file.write(output_data)

if __name__ == "__main__":
    main()
