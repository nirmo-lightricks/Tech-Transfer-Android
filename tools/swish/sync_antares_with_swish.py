import argparse
import json
import logging
from collections import OrderedDict
from enum import Enum
from pathlib import Path
from shutil import copy

logging.basicConfig(level=logging.INFO)

class Antares_Assets(Enum):
    MUSIC = ('MusicAssetsOriginMapping.json', ('Sounds'))
    VIDEO = ('VideoAndPhotosAssetsOriginMapping.json', ('Logos', 'Videos'))
    def __init__(self, json_file, asset_dirs):
        self._json_file = json_file
        self._asset_dirs = asset_dirs
    @property
    def json_file(self):
        return self._json_file
    @property
    def asset_dirs(self):
        return self._asset_dirs

def find_antares_asset(asset_key,asset, antares_template_assets_dir):
    for sub_dir in asset.asset_dirs:
        asset_sub_dir = antares_template_assets_dir / sub_dir
        glob_res = list(asset_sub_dir.glob(f'**/{asset_key}'))
        if glob_res:
            if len(glob_res) ==1:
                return glob_res[0]
            raise Exception(f"for key {asset_key} there are more than one result {glob_res}. This is ambigous")
    raise Exception(f" No result found for {asset_key}")

def copy_antares_asset_to_swish(antares_asset, facetune_template_assets_dir):
    target_file = facetune_template_assets_dir/ antares_asset.name
    logging.info(f'copying {antares_asset} to {target_file}')
    copy(antares_asset, target_file)




def sync_antares_with_swish(asset, mapping, antares_assets_dir, facetune_assets_dir):
     antares_template_assets_dir = antares_assets_dir/'Template Assets'
     facetune_template_assets_dir = facetune_assets_dir / 'template_assets'
     facetune_asset_files = {file.name:file for file in facetune_template_assets_dir.iterdir() if file.is_file()}
     assets_to_delete  = {facetune_asset_files[key] for key,url in mapping.items() if url.startswith('http') and key in facetune_asset_files}
     assets_to_copy   = {key for key,url in mapping.items() if not(url.startswith('http') or key in facetune_asset_files)}
     for asset_file in assets_to_delete:
         logging.info(f'removing asset file {asset_file}')
         asset_file.unlink()
     for asset_key in assets_to_copy:
         antares_asset = find_antares_asset(asset_key, asset, antares_template_assets_dir)
         copy_antares_asset_to_swish(antares_asset, facetune_template_assets_dir)
          
        

         






def get_json_mapping(asset, antares_assets_dir):
    json_file = antares_assets_dir / asset.json_file
    with open(json_file) as f:
        return json.load(f)
def verify_and_create_global_mapping(mappings):
    global_mapping = {}
    for mapping in mappings:
        intersection_keys = global_mapping.keys() & mapping.keys()
        if intersection_keys:
            raise Exception(f"keys {intersection_keys} are not unique")
        global_mapping.update(mapping)
    return global_mapping

def write_mapping_to_json(mapping, out_file):
    ordered_mapping = OrderedDict(sorted(mapping.items(), key=lambda i: i[0].casefold()))
    with open(out_file, 'w') as out:
        json.dump(ordered_mapping, out, indent=4)

def run_program(facetune_base_dir, antares_git_dir):
    facetune_base_dir = Path(facetune_base_dir)
    antares_base_dir = Path(antares_git_dir)
    antares_assets_dir = antares_base_dir/ 'Antares/Antares'
    facetune_assets_dir = facetune_base_dir/ 'swish/src/main/assets'
    
    out_file = facetune_assets_dir/ 'template_urls.json'
    mappings = []
    for asset in Antares_Assets:
        mapping = get_json_mapping(asset, antares_assets_dir)
        mappings.append(mapping)
        sync_antares_with_swish(asset, mapping, antares_assets_dir, facetune_assets_dir)

    global_mapping = verify_and_create_global_mapping(mappings)
    write_mapping_to_json(global_mapping, out_file)





parser = argparse.ArgumentParser(description='Sync Antares assets with swish')
parser.add_argument('facetune_base_dir', help='Facetune base dir')
parser.add_argument('antares_base_dir', help='Antares base dir')
args = parser.parse_args()

input("Make sure you updated the facetune android and swish git projects to the lastest version and press enter")

run_program(args.facetune_base_dir, args.antares_base_dir)
