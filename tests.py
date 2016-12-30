from processors.race_result_normalizer import RaceResultNormalizer
from settings import settings, secure_settings
import os

normalizer = RaceResultNormalizer(
    settings.TABLE_DEFS, secure_settings.DATA_FIXES, secure_settings.DB_LOCATION)


def test_distance_splitter():
    file_path = os.path.join(secure_settings.INPUT_DIRECTORY, 'raceResults_172.txt')
    table_data = normalizer.normalize_files([file_path])

    assert(len(table_data['race']) == 2)
    assert(len(table_data['result']) > 1000)
