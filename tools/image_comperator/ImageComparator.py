import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import imread
import os

# A script that reads two input image files and prints them out side by side, as well as the result of the subtraction
# between them.

def read_image(filename):
    float_matrix = (imread(filename)).astype(np.float64)
    return float_matrix / 255


def read_and_plot_images(file1, file2, output_file_name):
    print("Reading images...")
    image1 = read_image(file1)
    image2 = read_image(file2)
    print("Calculating Diff...")

    diff = abs(image2 - image1)
    title1 = os.path.split(file1)[1]
    title2 = os.path.split(file2)[1]

    plot(diff, title1, title2, image1, image2, output_file_name)


def plot(diff, title1, title2, image1, image2, output_file_name):
    print("Plotting...")
    fig = plt.figure()
    a = fig.add_subplot(1, 3, 1)
    imgplot = plt.imshow(image1)
    a.set_title(title1)
    plt.axis('off')
    a = fig.add_subplot(1, 3, 2)
    imgplot = plt.imshow(image2)
    a.set_title(title2)
    plt.axis('off')
    a = fig.add_subplot(1, 3, 3)
    imgplot = plt.imshow(diff)
    a.set_title("Diff")
    plt.axis('off')
    plt.savefig(output_file_name, bbox_inches='tight')
    plt.show()
    print("All Done! Check the output file for the results. ")


def parse_args():
    global file1, file2, output_file_name
    if len(sys.argv) != 4:
        print("Usage: image_file_name_1, image_file_name_2, output_image_file_name")
        return
    return sys.argv[1], sys.argv[2], sys.argv[3]


if __name__ == '__main__':
    file1, file2, output_file_name = parse_args()
    read_and_plot_images(file1, file2, output_file_name)
