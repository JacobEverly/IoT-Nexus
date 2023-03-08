# Independent-Research-Spring-2023 (Work in progress)


## Project Overview

![Screen Shot 2023-03-08 at 5 44 09 PM](https://user-images.githubusercontent.com/112036223/223868377-f5d89b26-6b18-43dd-9823-618377dfe689.png)

## Link to project board

https://www.notion.so/Blockchain-Independent-Research-38c4abe91db94eb8b41f2c6361302530

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

# Delete branch after pull request
git branch -d {branch name}
git checkout main
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

