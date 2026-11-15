# SBOM generator 
Generates a SBOM as a CSV and a JSON file in the specified directory by traversing subdirectories examining requirements.txt and package.json files.

The SBOM includes the following columns:
* Name
* Version
* Type (npm or pip)
* Absolute path to where the dependency was found

## How to run
With python 3, run the sbom.py file with a directory containing 1 or more source code repositories as argument, for example:
```
python3 sbom.py /home/Johannes/code/repos/
```

## Assumptions

* Assumes dependencies inside requirements.txt are managed by pip and dependencies inside package.json are managed by npm.
* Assumes requirements.txt files follow the format "name==version"