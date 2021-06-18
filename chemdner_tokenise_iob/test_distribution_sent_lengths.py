from srl_python_modules import Conll2003DatasetReader
import matplotlib.pyplot as plt
import os


def get_distribution(file_name):
    reader = Conll2003DatasetReader()
    lengths = []
    max_length = 0
    for instance in reader._read(file_name):
        lengths.append(len(instance.fields["tokens"]))
        if len(instance.fields["tokens"]) > max_length:
            max_length = len(instance.fields["tokens"])
    print("LENGTH:", file_name.split("/")[-1], str(max_length))
    print("NUMSENTS:", len(lengths))
    return lengths


def plot_distribution(distribution, bins=100, label="", range=(0, 300), color=None):
    plt.hist(distribution, bins=bins, alpha=0.7, label=label, density=False, range=range)
    plt.xlabel("Tokenized Sequence Length/Tokens")
    plt.ylabel("Number of Occurences")
    plt.xlim(0, 275)


def plot_distributions(file_names, labels=None):
    if not labels:
        labels = [file_name.split("/")[-1] for file_name in file_names]
    distributions = [get_distribution(file_name) for file_name in file_names]
    plt.hist(distributions, bins=100, label=labels, range=(0, 300), density=False, histtype='stepfilled', alpha=0.5)
    plt.xlabel("Tokenized Sequence Length")
    plt.ylabel("Number of Occurences")
    plt.legend()


if __name__ == "__main__":
    root_dir = "DIRECTORY UNDER WHICH THE TOKENIZED FILES ARE SAVED"
    file_names = ["LIST OF FILE NAMES WITHIN root_dir"]
    labels = ["LIST OF LABELS FOR PLOTTING"]
    plt.style.use(['seaborn-white', 'seaborn-paper'])
    plt.rc('font', family='serif')
    plt.rc('xtick', labelsize='x-small')
    plt.rc('ytick', labelsize='x-small')
    plt.figure(figsize=(4.8, 3.6))
    processed_file_names = file_names
    print(processed_file_names)
    plot_distributions(processed_file_names, labels)
    plt.savefig(os.path.join(root_dir, "comparison.pdf"))

