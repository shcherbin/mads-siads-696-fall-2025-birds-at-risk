# MADS SIADS 696: Milestone II - Predicting At Risk Bird Populations

By [Cyril Scerbin](mailto:kshcherb@umich.edu), [Jason Harris](mailto:harjason@umich.edu), [Emily Lerner](mailto:eslerner@umich.edu)

-----

<details>
<summary>Local Development Setup</summary>

This project uses Dev Containers in Visual Studio Code and Docker Desktop to provide a reproducible and isolated development environment.

Before starting, ensure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (required to run containers)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension for VS Code](https://code.visualstudio.com/docs/devcontainers/containers)

## Clone the Repository
First, fetch the project from GitHub:
```sh
git clone https://github.com/shcherbin/mads-siads-696-fall-2025-birds-at-risk.git
```

## Configuration
All configuraion parameters are stored in the `.env` file. 
Once the repo is cloned copy the `.env.example` and made the necessary changes.

```sh
cp .env.example .env
```

to access configration parameters in python use the following code snippet. 

```python
from birds.settings import load_settings

settings = load_settings()

print(settings.env)
print(settings.version)
```

## Accessing .env in the Terminal
Enable automatic environment variable loading with direnv:
```sh
direnv allow
```
Run this once per shell. If .env changes, you’ll be prompted to re-run the command.

## Dowload source datasets
To fetch the raw datasets needed for the project, simply run:

```sh
just dowload-source-data
```
This ensures that all required input data is available in the expected directories.


## Start the Development Environment
With Docker Desktop running, open the repository in VS Code. You should see a prompt to “Reopen in Container”.
Alternatively, use the Command Palette (Ctrl+Shift+P / Cmd+Shift+P) and select:
```
Dev Containers: Reopen in Container
```
This builds and runs the project’s development container, installing all dependencies inside an isolated environment.

</details>