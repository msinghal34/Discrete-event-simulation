import random

def get_random_variate(distribution, params):
    """
    Returns a random timeout estimate
    """
    if distribution == "exponential":
        return random.expovariate(params["lambd"])
    elif distribution == "uniform":
        return random.uniform(params["a"], params["b"])
    elif distribution == "deterministic":
        return params["c"]
    elif distribution == "c+exp":
        return params["c"] + random.expovariate(params["lambd"])