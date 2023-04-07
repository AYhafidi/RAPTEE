import random

def l2_sampler(stream, l2):
    #L2 sampler that takes a stream of identifiers and produces a sample list of size l2.
    samplers = [Sampler() for _ in range(l2)]
    for identifier in stream:
        for sampler in samplers:
            identifier = sampler(identifier)
        if all(sampler.done for sampler in samplers):
            break
    return [sampler.result for sampler in samplers]

class Sampler:
    #Sampler that chooses a hash function at random and stores the smallest identifier seen so far.

    def __init__(self):
        #Initialise chaque echantillonneur avec une fonction de hachage aleatoire, pas de resultat encore, et pas termine
        self.hash_function = random.randint(0, 1000000)
        self.result = None
        self.done = False

    def __call__(self, identifier):
        # Calcule la valeur de hachage de l'identifiant en utilisant la fonction de hachage de l'echantillonneur
        hash_value = hash(identifier) % self.hash_function
        if self.result is None or hash_value < self.hash_value:
            self.hash_value = hash_value
            self.result = identifier
        return self.result


stream = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
l2 = 3
sample = l2_sampler(stream, l2)
print(sample)





