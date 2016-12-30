import sys
import os
from processors.race_result_normalizer import RaceResultNormalizer
from settings import settings, secure_settings, manual_fixes


def main():
    if len(sys.argv) < 2:
        script_name = os.path.basename(__file__)
        print("Usage: " + script_name + " <directory>")
        input()
        return
    else:
        input_directory = sys.argv[1]

    normalizer = RaceResultNormalizer(settings.TABLE_DEFS, manual_fixes.fixes)

    normalizer.normalize(input_directory, secure_settings.DB_LOCATION)


if __name__ == "__main__":
    main()
