import os
import json
import csv
import sys
import subprocess

def read_requirements_file(path, sbom, commit_hash):
    """
    Reads a requirements.txt file and appends its dependencies to the SBOM.
    Dependencies are represented by a dictionary containing name, version, type, path, scope and commit hash.

    Expects the file to follow the format name==version. 
    """

    dependency_type = "pip"
    try:
        with open (path) as f:
            print("Opening", path)
            lines = f.readlines()

            for line in lines:
                line = line.strip('\n')
                name, version = line.split("==")
                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path, "scope" : "Unknown", "git commit" : commit_hash})

    except FileNotFoundError:
        print(f"File {path} was not found.")

def read_package_file(path, sbom, commit_hash):
    """
    Reads a package.json file and appends its dependencies to the SBOM.
    Dependencies are represented by a dictionary containing name, version, type, path, scope and commit hash.

    Includes both the dependencies and devDependencies from the package file.
    """

    dependency_type = "npm"
    try:
        with open(path) as f:
            print("Opening", path)
            data = json.load(f)

            # .get returns an empty dict if key is not found
            for name, version in data.get("dependencies", {}).items():
                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path, "scope" : "Production", "git commit" : commit_hash})

            for name, version in data.get("devDependencies", {}).items():
                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path, "scope" : "Development", "git commit" : commit_hash})

    except FileNotFoundError:
        print(f"File {path} was not found.")

def read_package_lock_file(path, sbom, commit_hash):
    """
    Reads a package-lock.json file and appends its dependencies to the SBOM.
    Dependencies are represented by a dictionary containing name, version, type, path, scope and commit hash.

    Ignores the root entry and iterates over every remaining entry in the "packages" dictionary.
    """

    dependency_type = "npm"
    try:
        with open(path) as f:
            print("Opening", path)
            data = json.load(f)

            for key, value in data.get("packages", {}).items():
                # Skip root entry
                if key == "":
                    continue

                # Remove node_modules/ from key to get name of package
                name = key.split("node_modules/")[-1]
                version = value["version"]

                if value.get("dev", False):
                    scope = "Development"
                else:
                    scope = "Production"

                sbom.append({"name" : name, "version" : version, "type" : dependency_type, "path" : path, "scope" : scope, "git commit" : commit_hash})

    except FileNotFoundError:
        print(f"File {path} was not found.")

def write_to_csv(sbom, path):
    """
    Writes SBOM to CSV file removing field names, one entry and row per dependency.
    Saves the file at the location of the path argument. 
    """

    csv_path = path + "sbom.csv"
    with open(csv_path, 'w', newline='') as f:
        fieldnames = ["name", "version", "type", "path", "scope", "git commit"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(sbom)
        print(f"Saved SBOM in CSV format to '{csv_path}'")

def write_to_json(sbom, path):
    """
    Writes SBOM to JSON file including field names.
    Saves the file at the location of the path argument. 
    """

    json_path = path + "sbom.json"
    with open(json_path, 'w') as f:
        json.dump(sbom, f)
        print(f"Saved SBOM in JSON format to '{json_path}'")

def remove_identical_entries(sbom):
    unique_sbom = []
    for dependency in sbom:
        if dependency not in unique_sbom:
            unique_sbom.append(dependency)

    return unique_sbom

def main():
    """
    Main function of the SBOM generator.
    Validates directory path given as command-line argument.
    Traverses subdirectories of the root directory searching for 
    requirements.txt, package.json and package-lock.json files.
    Writes dependencies found inside these files to SBOM files in CSV and JSON format.
    Removes identical entries.
    """

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
            # Retrieve git commit hash
            try:
                commit = subprocess.check_output('git log --format="%H" -n 1', shell=True, cwd=root, text=True).strip()

            except subprocess.CalledProcessError:
                print(f"Error: '{root}' is not a Git repository.")
                sys.exit(1)

            # Check for requirements.txt file
            if "requirements.txt" in files:
                requirements_path = root + "/requirements.txt"
                read_requirements_file(requirements_path, sbom, commit)

            # Check for package-lock.json file
            if "package-lock.json" in files:
                package_lock_path = root + "/package-lock.json"
                read_package_lock_file(package_lock_path, sbom, commit)

            # Check for package.json file
            elif "package.json" in files:
                package_path = root + "/package.json"
                read_package_file(package_path, sbom, commit)

    if len(sbom) == 0:
        print("Did not find any dependencies to list in SBOM.")
        sys.exit(0)

    sbom = remove_identical_entries(sbom)
    write_to_csv(sbom, path)
    write_to_json(sbom, path)

main()