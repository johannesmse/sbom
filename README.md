# SBOM generator 
Generates a SBOM as a CSV and a JSON file in the specified directory by traversing subdirectories examining requirements.txt, package-lock.json and package.json files.

The SBOM includes the following columns:
* Name
* Version
* Type (npm or pip)
* Absolute path to where the dependency was found
* Git commit hash of the source code repo

## How to run
With python 3, run the sbom.py file with a directory containing 1 or more source code repositories as argument, for example:
```
python3 sbom.py /home/Johannes/code/repos/
```

## Assumptions and limitations

* Assumes dependencies inside requirements.txt are managed by pip and dependencies inside package.json and package-lock.json are managed by npm.
* Assumes requirements.txt files follow the format "name==version".
* Assumes package-lock.json use lockfile version 3.
* If a package-lock.json file is found in a repository, the SBOM generator skips the package.json file. From the npm docs: "As of npm v7, lockfiles include enough information to gain a complete picture of the package tree, reducing the need to read package.json files". (https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json)