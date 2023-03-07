# Independent-Research-Spring-2023

## Create enviroment
```cmd
conda create -n {env} python=3.9
conda activate {env}
```
## Create and switch branch
```cmd
# Create branch
git branch {branch name}

# Switch branch
git checkout {branch name}

# Push to branch
git push -u origin {branch name} # for the first time
git push # for afterwards
```

Then do pull request for merging to main branch


## Git push
```cmd
git add {changed files}
git commit -m "{description}"
git push
```

## Install Python dependencies
```cmd
pip install -r requirement.txt
cd poseidon-hash
pip install -Ue .
```

