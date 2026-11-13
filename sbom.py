import os
import json
import csv

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
        print(f"Saved SBOM in CSV format to '{csv_path}")


def main():
    sbom = []
    path = "/home/jmse/code/projects/sbom/test_repos/"

    # Traverse subdirectories
    for root, dirs, files in os.walk(path):
        if root == path:
            print(f"Found {len(dirs)} repositories in '{path}'\n")
        else:
            # Check for requirements.txt file
            if "requirements.txt" in files:
                requirements_path = root + "/requirements.txt"
                read_requirements_file(requirements_path, sbom)

            # Check for package.json file
            if "package.json" in files:
                package_path = root + "/package.json"
                read_package_file(package_path, sbom)

    write_to_csv(sbom, path)




main()