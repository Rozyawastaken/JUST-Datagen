import os
import pickle


if __name__ == '__main__':
    # Replace 'your_file.cp' with your actual file path
    with open('G:\\SRNet_bg_images\\SynthText\\bg_data\\imnames.cp', 'rb') as file:
        data = pickle.load(file)

    output_path = 'G:\\SRNet_bg_images\\SynthText\\bg_data\\bg_img'  # Update to your output directory

    with open('Synthtext/files/background/labels.txt', 'w') as f:
        for filename in data:
            absolute_path = os.path.join(output_path, filename)
            f.write(absolute_path + '\n')

