import os


def count_consecutive_duplicates(file_path):
    count = 0
    prev_word = None
    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                _, word = parts
                if word == prev_word:
                    count += 1
                    print(f"Duplicate at line {idx - 1}: {word}")
                prev_word = word
    return count


def get_duplicate_files(txt_file_path):
    duplicate_files = []
    prev_word = None
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line_idx, line in enumerate(lines):
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                file_name, word = parts
                if word == prev_word:
                    duplicate_files.append((file_name, line_idx))
                prev_word = word
    return duplicate_files


def delete_files_and_filter_txt(folders, duplicate_files, txt_file_path):
    # Filter the i_t.txt to remove records of deleted files
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line_idx, line in enumerate(lines):
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            file_name, _ = parts
            # If the file is in the list of duplicates, skip adding it to the new lines
            if file_name not in [file[0] for file in duplicate_files]:
                new_lines.append(line)

    # Rewrite the updated i_t.txt without the deleted records
    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    # Now delete the duplicate files in the folders
    for folder in folders:
        for file_name, _ in duplicate_files:
            for file in os.listdir(folder):
                if file_name[:-4] in file:
                    file_to_delete = os.path.join(folder, file)
                    if os.path.exists(file_to_delete):
                        os.remove(file_to_delete)
                        print(f"Deleted duplicate file: {file_to_delete}")



if __name__ == '__main__':
    base_path = "F:\\YULA\\datasets\\testing\\test-15k-1"

    print(count_consecutive_duplicates(f"{base_path}\\i_t.txt"))

    txt_file_path = f"{base_path}\\i_t.txt"
    folders = [
        f"{base_path}\\i_s",
        f"{base_path}\\mask_s",
        f"{base_path}\\mask_t",
        f"{base_path}\\t_b",
        f"{base_path}\\t_f",
        f"{base_path}\\txt",
    ]

    # Example usage
    duplicate_files = get_duplicate_files(txt_file_path)
    print(duplicate_files)
    delete_files_and_filter_txt(folders, duplicate_files, txt_file_path)
