import json
import os
import random


elements = [
    "H",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Cl",
    "Al",
    "S",
    "P",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
]

includes_pdf = [True, False]

max_texture = [0.5, 0.6, 0.7, 0.8, 0.9]
min_domain_size = [3, 4, 5, 6, 7, 8]  # in nm
max_domain_size = [10, 20, 30, 40, 50]  # in nm
max_strain = [0.01, 0.02, 0.03, 0.04, 0.05]
num_patterns = [50, 100, 150, 200]
min_2_theta = [10, 13, 14, 20, 32, 40]
max_2_theta = [60, 63, 64, 76, 77, 80]
max_shift = [0.1, 0.2, 0.3, 0.4, 0.5]  # in degrees

num_epochs = [5, 10, 20, 30, 50, 100]
learning_rate = [0.001, 0.01, 0.1, 0.2, 0.5]
batch_size = [16, 32, 64, 128, 256]
test_fraction = [0.1, 0.2, 0.3, 0.4, 0.5]
training_accuracy = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
evaluation_accuracy = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]


def generate_model_entries(num_entries: int):
    os.makedirs("model_entries", exist_ok=True)
    for _ in range(num_entries):
        num_elements = random.randint(2, 4)
        elements_subset = random.sample(elements, num_elements)
        name = "auto_xrd_model"
        for el in elements_subset:
            name += f"_{el}"

        # make a dictionary for the model entry
        model_entry = {
            "data": {
                "m_def": "nomad_auto_xrd.schema_packages.schema.AutoXRDModel",
                "name": name,
                "includes_pdf": random.choice(includes_pdf),
                "simulation_settings": {
                    "min_angle": random.choice(min_2_theta),
                    "max_angle": random.choice(max_2_theta),
                    "max_texture": random.choice(max_texture),
                    "min_domain_size": random.choice(min_domain_size),
                    "max_domain_size": random.choice(max_domain_size),
                    "max_strain": random.choice(max_strain),
                    "num_patterns": random.choice(num_patterns),
                    "max_shift": random.choice(max_shift),
                },
                "training_settings": {
                    "num_epochs": random.choice(num_epochs),
                    "learning_rate": random.choice(learning_rate),
                    "batch_size": random.choice(batch_size),
                    "test_fraction": random.choice(test_fraction),
                },
                "evaluation_metrics": {
                    "accuracy": random.uniform(0.5, 0.99),
                },
                "training_metrics": {
                    "accuracy": random.uniform(0.8, 0.99),
                },
            },
            "results": {
                "material": {
                    "elements": elements_subset,
                },
            },
        }
        with open(f"model_entries/{name}.archive.json", "w", encoding="utf-8") as f:
            json.dump(model_entry, f, indent=4)


if __name__ == "__main__":
    num_entries = 53  # specify how many entries you want to generate
    generate_model_entries(num_entries)
    print(f"Generated {num_entries} model entries.")
