# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Documentation
- Enhance README and update CONTRIBUTING.md workflow diagram (_dd287c6_)

## [v1.5.8]
### 2025-07-24

### Documentation
- Update GPG signature example (_1f66a00_)
- add outline to README.md (_398dea9_)
- add outline to contribution guide (_5c6f128_)
- enhance and correct tag verification guide (_a8faa7d_)

### Miscellaneous
- misc: Bump version: 1.5.7 → 1.5.8 (_a56f7d6_)

## [v1.5.7]
### 2025-07-24

### Documentation
- fully document all environment variables (_b598787_)
- add detailed examples for verifying Git tags (_875bc58_)
- document optional environment variables (_940efa3_)
- reorganize and refine project structure guide (_28556ea_)
- fix Mermaid diagram syntax (_785f6b3_)
- detail the GPG signing process for releases (_5b66e43_)
- expand GPG installation instructions (_f676c64_)
- expand and detail commit message guidelines (_1df2948_)
- clarify how to get Telegram API credentials (_1fde1cd_)
- overhaul and detail contributing guide (_bb65e81_)

### Miscellaneous
- misc: Bump version: 1.5.6 → 1.5.7 (_49c05b9_)

## [v1.5.6]
### 2025-07-23

### Features
- **release:** enable GPG signing for version tags (_98d6745_)

### Documentation
- add guide for GPG signing releases (_3683c6c_)

### Miscellaneous
- misc: Bump version: 1.5.5 → 1.5.6 (_5af7688_)

## [v1.5.5]
### 2025-07-23

### Bug Fixes
- **versioning:** configure bump-my-version to stage its own changes (_efd1462_)

### Miscellaneous
- misc: Bump version: 1.5.4 → 1.5.5 (_994d7fa_)

## [v1.5.4]
### 2025-07-23

### Miscellaneous
- misc: Bump version: 1.5.3 → 1.5.4 (_5333dec_)

## [v1.5.3]
### 2025-07-23

### Features
- **versioning:** implement bump-my-version (_d4ee256_)

### Miscellaneous
- misc: Bump version: 1.5.2 → 1.5.3 (_fb1c8cd_)

## [v1.5.1]
### 2025-07-23

### Bug Fixes
- correct pyproject.toml syntax (_89ba9e0_)

### Documentation
- restructure documentation and add contribution guidelines (_fbddc54_)

## [v1.5.0]
### 2025-07-23

### Features
- add changelog and configure bump-my-version (_5c06566_)
- implement lru cache for dialog names (_9cc4063_)
- add traceback to main error log (_43f24e2_)
- add safeguard to prevent accidental deletion (_67be567_)
- improve retry decorator with jitter and backoff (_18cf4cd_)

### Bug Fixes
- configure bump-my-version to get logs from git (_1606b85_)
- uncomment params in env_example.txt (_de5bee0_)
- listen only to specified source channels (_0b43727_)
- pass stats_manager to MessageSynchronizer (_ea85b81_)
- improve shutdown handling in synchronizer (_05f34fb_)
- prevent caching of failed initial fetches (_8de4736_)

### Refactor
- simplify forwarder run method (_d736b59_)
- split _send_message into smaller methods (_449fe56_)
- use get_display_name in _get_dialog_name (_216596b_)
- remove redundant connection lock in forwarder (_21fa18b_)
- use specific exception handling in message_handler (_d035504_)
- improve client disconnection and error handling in launcher (_8e57580_)
- improve error handling and connection management in forwarder (_d224046_)

### Documentation
- add configuration section to readme (_228d181_)
- add explanation for MAX_CACHE_SIZE (_14c3bf8_)

### Miscellaneous
- chore(release): **release:** Bump version to 1.5.0 (_4d11c30_)
- misc: opt: reduce memory usage in synchronizer (_de9d373_)
- perf: remove connection lock from message_handler to improve performance (_832aacb_)

## [v1.4.0]
### 2025-07-21

### Features
- Add final runtime statistics summary (_8c901f6_)

### Miscellaneous
- chore(release): **release:** Bump version to 1.4.0 (_a5499cd_)

## [v1.3.0]
### 2025-07-21

### Bug Fixes
- Correctly set session parameters in TelegramClient (_2d9bc4f_)

### Refactor
- Isolate client creation and fix session info (_98b50e2_)

### Documentation
- Update launcher class docstring (_4f2f00c_)

### Miscellaneous
- chore(release): **release:** Bump version to 1.3.0 (_80d942b_)
- build: Configure automated version bumping (_ea5bea2_)
- build: Migrate bumpversion to pyproject.toml (_0e39991_)

## [v1.2.0]
### 2025-07-21

### Features
- Add dynamic OS and Python version to session info (_6b41cc8_)

### Miscellaneous
- build: Add bump-my-version for automated versioning (_0041a72_)

## [v1.1.0]
### 2025-07-21

### Features
- Improve donations section and UX (_5ddfedc_)
- Add styled donations page (_aea85ae_)

### Bug Fixes
- requirments.txt - python-dotenv (_398e0f3_)

### Refactor
- Implement robust, modular architecture (_0bf0b4e_)
- Centralize send logic and add self-healing (_7733d3d_)

### Documentation
- Update Project Structure in README (_dfbb2f1_)
- badges fix (_9517992_)

### Miscellaneous
- misc: update .gitignore for (temp) (_d158d07_)

