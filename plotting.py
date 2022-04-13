import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter


def combine_guesses():
    all_guesses = []
    for i in range(5):
        FileStore = open(f"stored_objects/guesses_{i}.pickle", "rb")
        guesses = pickle.load(FileStore)
        FileStore.close()
        all_guesses.extend(guesses)

    FileStore = open(f"stored_objects/ht_min_parity_guesses_final.pickle", "wb")
    pickle.dump(all_guesses, FileStore)
    FileStore.close()


def plot_games(num_guesses, display_name=None):
    games_by_score = Counter(num_guesses)
    for i in range(101):
        if i not in games_by_score.keys():
            games_by_score[i] = 0
    games_by_score = dict(sorted(games_by_score.items(), key=lambda item: item[0]))
    if display_name:
        plt.plot(games_by_score.keys(), games_by_score.values(), label=display_name)
    else:
        plt.plot(games_by_score.keys(), games_by_score.values())


def plot_all_games(file_names, display_names):
    for file_name, display_name in zip(file_names, display_names):
        FileStore = open(f"stored_objects/{file_name}.pickle", "rb")
        guesses = pickle.load(FileStore)
        FileStore.close()
        plot_games(guesses, display_name)
    plt.legend(loc="upper left")


def plot_all_cdfs(file_names, display_names):
    for filename, display_name in zip(file_names, display_names):
        FileStore = open(f"stored_objects/{filename}.pickle", "rb")
        guesses = pickle.load(FileStore)
        FileStore.close()
        sns.kdeplot(data=[0] + guesses + [100], cumulative=True, clip=(0, 101), label=display_name)
    plt.legend(loc="upper left")


file_names = ["random_guesses_final", "ht_guesses_final", "ht_min_parity_guesses_final", "prob_guesses_final"]
display_names = ["Random", "Hunt / Target", "Hunt / Target Minimum", "Probabilistic"]
num = 4
# plot_all_games(file_names[:num], display_names[:num])
plot_all_cdfs(file_names[:num], display_names[:num])
plt.show()

