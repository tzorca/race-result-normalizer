import os

DATA_DIRECTORY = "./data/"

data_files = os.listdir(DATA_DIRECTORY)

for filename in data_files:
    with open(DATA_DIRECTORY + filename, "r") as f:
        print(f.read())
