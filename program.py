from processors.race_result_normalizer import RaceResultNormalizer
from settings import settings, secure_settings


def main():
    normalizer = RaceResultNormalizer(settings.TABLE_DEFS, secure_settings.DATA_FIXES, secure_settings.DB_LOCATION)
    normalizer.normalize_directory(secure_settings.INPUT_DIRECTORY)


if __name__ == "__main__":
    main()
