# NOMAD Dev Distribution

Below are instructions for how to create a dev env for developing NOMAD and nomad plugins.

### Basic infra

1. Make sure you have [docker](https://docs.docker.com/engine/install/) installed.
   Docker nowadays comes with `docker compose` built in. Prior, you needed to
   install the stand-alone [docker-compose](https://docs.docker.com/compose/install/).

2. Make sure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
   The standalone installer or a global installation is the recommended way.
   (`brew install uv` on macOS or `dnf install uv` on Fedora).

3. Clone the repository.

4. _On Linux only,_ recursively change the owner of the `.volumes` directory to the nomad user (1000)

```sh
sudo chown -R 1000 .volumes
```

5. Run the docker containers with docker compose in detached (--detach or -d) mode

```sh
docker compose up -d
```

To shutdown the containers:

```sh
docker compose down
```

## Developing nomad + plugins locally.

This guide explains how to set up a streamlined development environment for nomad-lab and its plugins using uv workspaces.
This approach eliminates the need for multiple pip install commands by leveraging a monorepo and a single installation step.

In this example, we'll set up the development environment for a developer working on the following computational parsers:

- nomad-parser-plugins-electronic
- nomad-parser-plugins-atomistic
- nomad-parser-plugins-workflow
- nomad-parser-plugins-database

### Step-by-Step Setup

1. Clone the Monorepo

Start by forking and cloning the main repository (e.g., dev_distro) that will house all your plugins.

```bash
git clone https://github.com/your-username/dev_distro.git
cd dev_distro
```

2. Add Local Plugins

Add the parser plugin repositories to the packages/ directory, either as submodules or direct clones.

Option 1: Using git submodule:

```bash
git submodule add https://github.com/package_name.git packages/package_name
```

Option 2: Using git clone:

```bash
git clone https://github.com/package_name.git packages/package_name
```

Repeat for all local dev packages (e.g., nomad-lab, nomad-parser-plugins-electronic, nomad-parser-plugins-atomistic, etc.).

3. Modify pyproject.toml

Ensure uv recognizes the local packages by modifying the `pyproject.toml`:

```toml
[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
nomad-lab = { workspace = true }
nomad-parser-plugins-electronic = { workspace = true }
nomad-parser-plugins-atomistic = { workspace = true }
nomad-parser-plugins-workflow = { workspace = true }
nomad-parser-plugins-database = { workspace = true }
```

4. Install Dependencies

Run the following command to install all dependencies, including the local packages in editable mode:

```bash
uv sync --extra-all
```

5. Running `nomad`.

```bash
uv run nomad --help
```

### Day-to-Day Development

After the initial setup, here’s how to manage your daily development tasks.

1. Installing Dependencies

If you've added new dependencies or made changes to your environment, install or update them by running:

```bash
uv sync --extra-all
```

This will sync all packages and ensure everything is installed in editable mode.

2. Running Tests

To run tests across the project, use the uv run command to execute pytest in the relevant directory. For instance:

```bash
uv run --directory packages/package_name pytest
```

This allows you to run tests for a specific parser or package. For running tests across all packages, simply repeat the command for each directory.

3. Making Code Changes

Since all packages are installed in editable mode, changes you make to the code are immediately reflected. Edit your code and rerun tests or the application as needed, without needing to reinstall the packages.

4. Linting & Code Formatting

To check for code style issues using ruff, run the following command:

```bash
uv run ruff check .
```

This will lint all files.

For auto-formatting:

```bash
uv run ruff format .
```

5. Adding New Plugins

To add a new package, follow setup guide and add it into the packages/ directory and ensure it's listed in pyproject.toml under [tool.uv.sources]. Then, install it by running:

```bash
uv sync --extra-all
```

6. Keeping Up-to-Date

To pull updates from the main repository and submodules, run:

```bash
bash
git pull --recurse-submodules
```

Afterward, sync your environment:

```bash
uv sync --extra-all
```

Benefits

- Single-Step Installation: Install all dependencies and local plugins with one command.
- Editable Mode: Local plugins are installed in editable mode, allowing immediate reflection of code changes.
- Centralized Development: Manage all your projects in one monorepo.
