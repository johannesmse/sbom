import os
import json
import csv
import sys

def read_requirements_file(path, sbom):
    """
    Reads a file at path given as argument and saves 
    name, version, type and path to dictionary given as argument.
    This method expects the text format to match the standard pip freeze requirements.txt format created by pip. 
    """

    dependency_type = "pip"

    try:
        with open (path) as f:
            print("Opening", path)
            lines = f.readlines()

            for line in lines:
                line = line.strip('\n')
                name, version = line.split("==")
                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path})

    except FileNotFoundError:
        print(f"File {path} was not found.")

def read_package_file(path, sbom):
    dependency_type = "npm"

    try:
        with open(path) as f:
            print("Opening", path)
            data = json.load(f)

            # .get returns an empty dict if key is not found
            # reads dependencies into sbom
            for name, version in data.get("dependencies", {}).items():
                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path})

            # reads devDependencies into sbom
            for name, version in data.get("devDependencies", {}).items():
                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path})

    except FileNotFoundError:
        print(f"File {path} was not found.")

def write_to_csv(sbom, path):
    csv_path = path + "sbom.csv"

    with open(csv_path, 'w', newline='') as f:
        fieldnames = ["name", "version", "type", "path"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(sbom)
        print(f"Saved SBOM in CSV format to '{csv_path}'")

def write_to_json(sbom, path):
    json_path = path + "sbom.json"

    with open(json_path, 'w') as f:
        json.dump(sbom, f)
        print(f"Saved SBOM in JSON format to '{json_path}'")


def main():
    if len(sys.argv) != 2:
        print(f"Error: expected 1 argument (directory path), but {len(sys.argv) - 1} were given.")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print("Error: the specified path does not exist.")
        sys.exit(1)

    if not os.path.isdir(path):
        print("Error: the specified path is not a directory.")
        sys.exit(1)

    if path[-1] != '/':
        path += '/'


    sbom = []
    # Traverse subdirectories
    for root, dirs, files in os.walk(path):
        if root == path:
            print(f"Found {len(dirs)} repositories in '{path}'\n")

            if len(dirs) == 0:
                print("Error: no subdirectories in the specified path was found.")
                sys.exit(1)
                
        else:
            # Check for requirements.txt file
            if "requirements.txt" in files:
                requirements_path = root + "/requirements.txt"
                read_requirements_file(requirements_path, sbom)

            # Check for package.json file
            if "package.json" in files:
                package_path = root + "/package.json"
                read_package_file(package_path, sbom)

    if len(sbom) == 0:
        print("Did not find any dependencies to list in SBOM.")
        sys.exit(0)

    write_to_csv(sbom, path)
    write_to_json(sbom, path)


main()