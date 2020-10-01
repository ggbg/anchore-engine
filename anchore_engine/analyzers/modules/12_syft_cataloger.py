#!/usr/bin/env python3

import os
import sys
import collections

import anchore_engine.analyzers.utils
from anchore_engine.clients.syft_wrapper import catalog_image



def handle_gem(artifact):
    return {
            'name': artifact['name'],
            'versions': [artifact['version']],
            'latest': artifact['version'],
            'sourcepkg': artifact['name'],
            'files': [], # TODO enhance
            'origins': [],
            'lics': [], # TODO enhance
            'type': 'gem',
        }

def filter_artifacts(artifact):
    # TODO: allow for more types as we go
    if artifact['type'] in ['bundle']:
        return True
    return False

def fetch_analysis(image_path):
    all_results = catalog_image(image_path)
    print(len(all_results['artifacts']))

    partial_results = filter(filter_artifacts, all_results['artifacts'])

    handlers = {
        'gem': handle_gem,
        # TODO: add handlers as we go...
    }

    typeLookup = {
        'bundle': 'gem',
        # TODO: map all of the types out here...
    }

    # transform output into analyzer-module/service json doc
    packages_by_type = collections.defaultdict(list)
    for artifact in partial_results:
        artifact_type = artifact['type']
        engine_type = typeLookup[artifact_type]
        engine_artifact = handlers[engine_type](artifact)
        packages_by_type[engine_type].append(engine_artifact)

    return packages_by_type

def write_results(results, output_dir):
    # write out results
    output_file = os.path.join(output_dir, 'syft_packages')
    anchore_engine.analyzers.utils.write_kvfile_fromdict(output_file, results)

def main(image_path, output_dir):
    results = fetch_analysis(image_path)
    if results:
        write_results(results, output_dir)
    else:
        print("no results")

# if __name__ == "__main__":

#     try:
#         config = engine_type.analyzers.utils.init_analyzer_cmdline(sys.argv, "syft_cataloger")
#     except Exception as err:
#         # TODO: improve me
#         print(str(err))
#         sys.exit(1)

#     image_path = config['dirs']['copydir']
#     output_dir = config['dirs']['outputdir']

#     main(image_path, output_dir)

main(sys.argv[1], ".")
