import numpy as np
import matplotlib.pyplot as plt


def read_binary(filename):
    with open(filename, "rb") as f:
        data = f.read()
    numbers = np.array(list(data))
    numbers = np.reshape(numbers, (-1, 4))

    pos1 = numbers[:, 1]
    pos2 = numbers[:, 2]
    pos3 = numbers[:, 3]

    plt.plot(pos1, ".")
    plt.savefig("pos1.png")
    plt.close()

    intensity = numbers[:, 0]

    plt.plot(pos1, ".")
    plt.savefig("intensity.png")
    plt.close()

    intensity = np.reshape(intensity, (775, 2080))
    plt.imshow(intensity, cmap="gray")
    plt.savefig("Image0.png")
    plt.close()
    plt.imshow(np.log10(intensity), cmap="gray")
    plt.savefig("Image0_log.png")
    plt.close()

    print("pos1:", np.min(pos1), np.max(pos1), np.count_nonzero(pos1))
    print("pos2:", np.min(pos2), np.max(pos2))
    print("pos3:", np.min(pos3), np.max(pos3))
    print("intensity:", np.min(intensity), np.max(intensity))


if __name__ == "__main__":
    read_binary("Image0.bin")
