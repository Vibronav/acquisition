# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased] - yyyy-mm-dd
### Added
### Deleted
### Changed
### Fixed

## [1.9.1] - 2025-07-31
### Fixed
- Detecting chirp signal in sync tool

## [1.9.0] - 2025-07-04
### Added
- Specifying manual recordings time
- New options for filename
- Real-time waveform scaling
- More informations in GUI on errors in app
- Shortcut for start/stop recording
- Option for deleting last recording
### Changed
- Set speed of dobot from 1-100 instead of hardcoded values

## [1.8.1] - 2025-06-16
### Fixed
- improve doing series of punctures by dobot
- saving recordings faster

## [1.8.0] - 2025-06-16
### Added
- Add recording videos/audio without dobot
- Add on live sounds from microphone

## [1.7.0] - 2025-06-10
### Added
- Second camera integration
- Displaying signals from microphone on live
- Steering dobot by specifying points to move
### Changed
- Run all experiment instead of start recording for 1 iteration by web app
- Download videos to specified folder

## [1.6.0]
### Added
- Synchronization for event annotations.

## [1.5.1]
### Fixed
- Error handling for synchronization endpoint.

## [1.5.0]
### Added
- `vnav_audio_video_sync` endpoint for synchronization of video and audio annotations.

## [1.4.0]
### Added
- Spikes/clips removal
### Fixed
- Too long delay between recording command and playing sync sound.

## [1.3.1]
### Fixed
- Not showing error when no files are saved.
- Corrected delays between sending commands and playing sync sound.

## [1.3.0]
### Added
- Automatic signal postprocessing
- Button for deleting last recording
### Changed
- Visible names of audio/video devices

## [1.2.0] - 2024-01-13
### Added
- Automated configuration of RaspberryPi
- Information about failed recording
- `local_dir` and `remote_dir` in configuration
### Changed
- Interface enhancement
- Video recording resolution (1280x720)

## [1.1.0] - 2023-12-14
### Added
- Support for two audio channels
### Fixed
- Camera is initialized at startup

## [1.0.0] - 2023-12-12
### Added
- External setup file
### Deleted
- Support for Jupyter

## [0.3.0] - 2023-12-02
### Added
- Choice of camera, unified file names for audio and video.

## [0.2.0] - 2023-11-18
### Added
- Working remote control of Raspberry PI

## [0.1.0] - 2023-11-04
### Added
- Initial version of the tool.