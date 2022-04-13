import pickle
from battleship_simulations import plot_games
import matplotlib.pyplot as plt
from statistics import median


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


def plot_guesses():
    FileStore = open(f"stored_objects/random_guesses_final.pickle", "rb")
    random_guesses = pickle.load(FileStore)
    FileStore.close()
    plot_games(random_guesses)

    FileStore = open(f"stored_objects/ht_guesses_final.pickle", "rb")
    ht_guesses = pickle.load(FileStore)
    FileStore.close()
    plot_games(ht_guesses)

    FileStore = open(f"stored_objects/ht_min_parity_guesses_final.pickle", "rb")
    ht_mp_guesses = pickle.load(FileStore)
    FileStore.close()
    plot_games(ht_mp_guesses)

    FileStore = open(f"stored_objects/prob_guesses_final.pickle", "rb")
    prob_guesses = pickle.load(FileStore)
    FileStore.close()
    plot_games(prob_guesses)

    plt.show()


combine_guesses()
plot_guesses()
