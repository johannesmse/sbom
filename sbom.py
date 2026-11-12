
sbom = {}
dependency_type = "pip"
path = "requirements.txt"

try:
    with open (path) as f:
        lines = f.readlines()

        for line in lines:
            line = line.strip('\n')
            name, version = line.split("==")
            sbom[name] = version, dependency_type, path

except FileNotFoundError:
    print(f"File {path} was not found.")
