# OpenTTD MSX Creator

## Introduction

<details>
  <summary>What is an MSX?</summary>

An MSX pack in OpenTTD (Open Transport Tycoon Deluxe) is a collection of music tracks formatted for the game. OpenTTD is an open-source game where players manage transport networks. The MSX packs are used to replace the default game music with custom tracks. These packs consist of MIDI files and a playlist file which contains the metadata.

</details>

## Installation

- This script was made with Python 3.10.7.
- Clone and enter this repository.
- Run `pip install -r requirements.txt`

## Usage

Creating an MSX requires a few different steps. This Python script does most of the work automatically.

1. Create a folder inside `music/` and place your `.mid` files inside.
   - The name's of your files will be the title of your songs in the game.
2. Run `python msxmake.py`
3. Select the folder with your songs and the theme song that will only be available in the title screen.
4. Enter the metadata for the MSX:
   - name, shortname, version, description, and origin
5. Find your MSX in the `msx/` folder and move it to your OpenTTD's `baseset/` folder.
