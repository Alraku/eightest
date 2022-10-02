# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

# v0.3.0 - (2022-10-01)

This version brings improvements in test running and small fixes.

## Major Improvements:
* Added rerun functionality in https://github.com/Alraku/eightest/pull/3
* Changelog update in https://github.com/Alraku/eightest/pull/4
* Refactored project file structure, added .toml, .ini files in https://github.com/Alraku/eightest/pull/6
* Added timeout feature in https://github.com/Alraku/eightest/pull/8

## Bug Fixed:
* Fixed lacking space in messages in https://github.com/Alraku/eightest/pull/7
* Fixed no os-dependent path creation in https://github.com/Alraku/eightest/pull/5

**Full Changelog**: https://github.com/Alraku/eightest/compare/v0.2.1...v0.2.2

# v0.2.1 - (2022-09-23)

This version presents first implementation of custom decorators.

## Major changes:
- Added custom Decorator Template along with specific examples in [#2](https://github.com/Alraku/sprinter/pull/2)

**Full Changelog**: https://github.com/Alraku/sprinter/compare/v0.2.0...v0.2.1

# v0.2.0 - (2022-09-22)

This version contains improved logging capabilities along with better results gathering from processes.

## Major changes:
- Refactored Logger initialization, added new methods: start, end and exception.
- Refactored Process module so it is more readable now.
- Added result creation on the side of process and returning it back to runner.

**Full Changelog**: https://github.com/Alraku/sprinter/compare/v0.1.0...v0.2.0

# v0.1.0 - (2022-09-14)

This is first pre-release version of Sprinter software. From now on all major changes will be listed in this changelog file.

## Major changes:

- Test discovery module ([source/search.py](https://github.com/Alraku/sprinter/blob/main/source/search.py))
- Parallel test execution ([source/runner.py](https://github.com/Alraku/sprinter/blob/main/source/runner.py))
- Logging to console and file 

**Full Changelog**: https://github.com/Alraku/sprinter/commits/v0.1.0

# v0.0.x (2022-09-06)

## Major changes:

- Added process duration.
- Code refactor

# v0.0.x (2022-09-05)

## Major changes:

- Added custom logger to process.