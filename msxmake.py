import os
import hashlib
from typing import Dict, Callable
import inquirer
import shutil


class Result:
    def __init__(self, value, is_success=True):
        self.value = value
        self.is_success = is_success

    def bind(self, func: Callable[[any], 'Result']):
        if self.is_success:
            try:
                return func(self.value)
            except Exception as e:
                return Result(e, False)
        else:
            return self

    def map(self, func: Callable[[any], any]):
        if self.is_success:
            try:
                return Result(func(self.value), True)
            except Exception as e:
                return Result(e, False)
        else:
            return self

    def unwrap(self):
        if self.is_success:
            return self.value
        else:
            raise Exception(f"Unwrapped a failure: {self.value}")


def get_md5_hash(file_path: str) -> Result:
    return Result(hashlib.md5(open(file_path, 'rb').read()).hexdigest())


def clean_filename(filename: str) -> Result:
    return Result('_'.join(filename.replace('.mid', '').strip().lower().split()) + '.mid')


def choose_item(base_dir: str, message: str, file_filter: str | None = None) -> Result:
    try:
        items = [f for f in os.listdir(base_dir) if os.path.isdir(
            os.path.join(base_dir, f)) or (file_filter and f.endswith(file_filter))]
        answers = inquirer.prompt(
            [inquirer.List('selected', message=message, choices=items)])
        return Result(answers['selected'])
    except Exception as e:
        return Result(e, False)


def setup_output_directory(base_dir: str, metadata_name: str) -> Result:
    return Result(os.makedirs(os.path.join(base_dir, '..', 'msx', metadata_name), exist_ok=True) or os.path.join(base_dir, '..', 'msx', metadata_name))


def copy_files_to_output(input_folder_path: str, output_folder_path: str) -> Result:
    try:
        for file_name in os.listdir(input_folder_path):
            if file_name.endswith('.mid'):
                shutil.copy2(os.path.join(input_folder_path, file_name), os.path.join(
                    output_folder_path, clean_filename(file_name).unwrap()))
        return Result(None)
    except Exception as e:
        return Result(e, False)


def get_metadata(name: str) -> Result:
    try:
        metadata = {
            'name': input(f"Enter the MSX name (default `{name}`): ") or name,
            'shortname': input(f"Enter the MSX shortname (default `{name}`): ") or name,
            'version': input("Enter the MSX version (default `1`): ") or '1',
            'description': input("Enter the MSX description (default `Made with https://github.com/connorswis/msx-creator`): ") or 'Made with github.com/connorswis/msx-creator',
            'origin': input("Enter the MSX origin URL (optional): ") or '\"\"'
        }
        return Result(metadata)
    except Exception as e:
        return Result(e, False)


def assign_tracks(folder_path: str, theme_song: str, include_theme_song: bool, clean_filename_fn, get_md5_hash_fn) -> Result:
    try:
        categories = ['old', 'new', 'ezy']
        category_limits = {category: 10 for category in categories}
        tracks = {f"{cat}_{i}": '' for cat in categories for i in range(10)}
        hashes, names = {}, {}

        theme_song_clean = clean_filename_fn(theme_song).unwrap()
        theme_song_details = {'theme': theme_song_clean}
        full_theme_path = os.path.join(folder_path, theme_song)
        hashes[theme_song_clean] = get_md5_hash_fn(full_theme_path).unwrap()
        names[theme_song_clean] = theme_song[:-4]

        track_counter = {category: 0 for category in categories}
        if include_theme_song:
            track_id = f"new_{track_counter['new']}"
            tracks[track_id] = theme_song_clean
            track_counter['new'] += 1

        for filename in sorted(f for f in os.listdir(folder_path) if f.endswith('.mid') and f != theme_song):
            for category in categories:
                if track_counter[category] < category_limits[category]:
                    track_id = f"{category}_{track_counter[category]}"
                    cleaned_filename = clean_filename_fn(filename).unwrap()
                    tracks[track_id] = cleaned_filename
                    track_counter[category] += 1
                    full_file_path = os.path.join(folder_path, filename)
                    hashes[cleaned_filename] = get_md5_hash_fn(
                        full_file_path).unwrap()
                    names[cleaned_filename] = filename[:-4]
                    break

        return Result((theme_song_details, tracks, hashes, names))
    except Exception as e:
        return Result(e, False)


def create_obm_file(output_folder_path: str, content: str) -> Result:
    try:
        with open(os.path.join(output_folder_path, os.path.basename(output_folder_path) + '.obm'), 'w') as file:
            file.write(content)
        return Result(None)
    except Exception as e:
        return Result(e, False)


def generate_output(metadata: Dict[str, str], theme_song_details: Dict[str, str], tracks: Dict[str, str], hashes: Dict[str, str], names: Dict[str, str]) -> Result:
    try:
        result = "[metadata]\n"
        result += f"name        = {metadata['name']}\n"
        result += f"shortname   = {metadata['shortname']}\n"
        result += f"version     = {metadata['version']}\n"
        result += f"description = {metadata['description']}\n\n"

        result += "[files]\n"
        result += '\n'.join(f"{key} = {value}" for key,
                            value in theme_song_details.items()) + "\n"
        result += '\n'.join(f"{key} = {value}" for key,
                            value in tracks.items()) + "\n"

        result += "\n[md5s]\n"
        result += '\n'.join(f"{file} = {hash_val}" for file,
                            hash_val in hashes.items()) + "\n"

        result += "\n[names]\n"
        result += '\n'.join(f"{file} = {name}" for file,
                            name in names.items()) + "\n"

        result += "\n[origin]\n"
        result += f"default = {metadata['origin']}\n"
        return Result(result)
    except Exception as e:
        return Result(e, False)


def main():
    base_dir = os.path.abspath('music')

    (choose_item(base_dir, "Select the folder")
        .bind(lambda selected_folder: Result(os.path.join(base_dir, selected_folder))
              .bind(lambda selected_folder_path: get_metadata(selected_folder)
              .bind(lambda metadata: setup_output_directory(base_dir, metadata['name'])
                    .bind(lambda output_folder: copy_files_to_output(selected_folder_path, output_folder)
                    .bind(lambda _: choose_item(selected_folder_path, "Select the theme song (.mid file)", file_filter='.mid')
                          .bind(lambda theme_song: Result(inquirer.prompt([inquirer.Confirm('include', message="Include the theme song in the in-game music?", default=True)]))
                          .bind(lambda answer: assign_tracks(selected_folder_path, theme_song, answer['include'], clean_filename, get_md5_hash)
                                .bind(lambda track_data: generate_output(metadata, *track_data)
                                .bind(lambda content: create_obm_file(output_folder, content)
                                      .map(lambda _: print("Output written to:", os.path.join(output_folder, os.path.basename(output_folder) + '.obm')))))))))))))


if __name__ == '__main__':
    main()
