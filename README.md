### Quickfix app

Electronics repair app

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit


 
## Quickfix Multi-Site Setup

This document explains how I set up two sites on the same bench and configured them for development and production.

## 1. Sites Created

I created two sites on my bench:

 `quickfix-dev.localhost` - for development  
 `quickfix-prod.localhost` - for production  
Both sites have the Quickfix app installed.


## 2. Developer Mode

On the dev site only, I enabled developer mode by adding "developer_mode": 1 in site_config.json. This allows Python files to auto-reload and disables production asset caching.  
I did not enable developer mode on the production site because it would show error tracebacks to users and disable caching, which is unsafe.


## 3. Shared Configuration

In `common_site_config.json`, I added:
"db_host": "localhost"


1. site_config.json - is per-site configuration (DB name,DB password, developer mode). common_site_config.json- contains settings shared across all sites (like db_host,).  
2. Putting secrets in common_site_config.json is risky because all sites share it and it could be accidentally checked into git.  
3. Developer mode on dev site allows auto-reloading of Python files and disables asset caching. Never enable on production.  
4. bench start launches 4 processes: web (handles HTTP requests), worker (processes background jobs), scheduler (runs scheduled tasks), socketio (real-time communication). If the worker crashes, background jobs are not processed until the worker is restarted. 