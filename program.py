from processors.race_result_normalizer import RaceResultNormalizer
from settings import settings, secure_settings, manual_fixes


def main():
    normalizer = RaceResultNormalizer(settings.TABLE_DEFS, manual_fixes.fixes)
    normalizer.normalize(secure_settings.INPUT_DIRECTORY, secure_settings.DB_LOCATION)


if __name__ == "__main__":
    main()
