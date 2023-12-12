from dataclasses import dataclass
import json

@dataclass
class Settings:
    thread_count: int = 4
    page_load_seconds: int = 30
    input_file_path: str = './input/rsid_values.xlsx'
    output_file_path: str = './output/output.xlsx'
    starting_url: str = 'https://www.ensembl.org/index.html'
    population: str = ''
    do_end_checkup: str = 'true'
    options: list = None

def load_settings(input_file_path: str = None):
    return Settings(**load_settings_from_file(input_file_path))

def load_settings_from_file(input_file_path: str = None):
    if input_file_path is None:
        input_file_path = Settings().input_file_path
    return load_settings_from_file_path(input_file_path)

def load_settings_from_file_path(input_file_path: str):
    return load_settings_from_file_contents(read_file_contents(input_file_path))

def load_settings_from_file_contents(file_contents: str):
    return json.loads(file_contents)

def read_file_contents(input_file_path: str):
    with open(input_file_path, 'r') as file:
        return file.read()
    

