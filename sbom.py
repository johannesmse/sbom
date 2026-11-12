import os

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

                # Check if dependency already added
                if name not in sbom:
                    sbom[name] = [(version, dependency_type, path)]
                else:
                    sbom[name].append((version, dependency_type, path))

    except FileNotFoundError:
        print(f"File {path} was not found.")

def main():
    sbom = {}
    path = "/home/jmse/code/projects/sbom/test_repos"

    # Traverse subdirectories
    for root, dirs, files in os.walk(path):
        if root == path:
            print(f"Found {len(dirs)} repositories in '{path}'")
        else:
            # Check for requirements file
            if "requirements.txt" in files:
                requirements_path = root + "/requirements.txt"
                read_requirements_file(requirements_path, sbom)


main()