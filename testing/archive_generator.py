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

min_2_theta = [10, 20, 32]
max_2_theta = [60, 76, 80]

num_epochs = [20, 30, 50]


def generate_model_entries(num_entries: int):
    os.makedirs("model_entries", exist_ok=True)
    for _ in range(num_entries):
        num_elements = random.randint(2, 4)
        elements_subset = random.sample(elements, num_elements)
        name = "auto_xrd_model"
        for el in elements_subset:
            name += f"_{el}"
        includes_pdf_choice = random.choice(includes_pdf)
        min_angle_choice = random.choice(min_2_theta)
        max_angle_choice = random.choice(max_2_theta)
        num_epochs_choice = random.choice(num_epochs)

        # make a dictionary for the model entry
        model_entry = {
            "data": {
                "m_def": "nomad_auto_xrd.schema.AutoXRDModel",
                "name": name,
                "includes_pdf": includes_pdf_choice,
                "simulation_settings": {
                    "min_angle": min_angle_choice,
                    "max_angle": max_angle_choice,
                },
                "training_settings": {
                    "num_epochs": num_epochs_choice,
                },
            },
            "results": {
                "material": {
                    "elements": elements_subset,
                },
            },
        }
        with open(f"model_entries/{name}.archive.json", "w") as f:
            json.dump(model_entry, f, indent=4)


if __name__ == "__main__":
    num_entries = 36  # specify how many entries you want to generate
    generate_model_entries(num_entries)
    print(f"Generated {num_entries} model entries.")
