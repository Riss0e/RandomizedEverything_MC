import os
import json
import random
import shutil

version = "0.8.1"

def WriteFileJson(path, filename, data):
    with open(os.path.join(path, filename), "w") as file:
        json.dump(data, file, indent=4)

def WriteFile(path, filename, data):
    with open(os.path.join(path, filename), "w") as file:
        file.write(data)

def recursive_loot(data, all):
    if isinstance(data, dict):
        for name, value in data.items():
            if name == "name":
                data[name] = f"minecraft:{random.choice(all)}"
            else:
                recursive_loot(value, all)
    elif isinstance(data, list):
        for item in data:
            recursive_loot(item, all)

print(f"Welcome to the Randomized Everything Generator {version} by Rissoe")

path_dir = os.path.dirname(os.path.abspath(__file__))
path_pack = os.path.join(path_dir, "RandomizedEverything")
path_tmp = os.path.join(path_dir, "Version")
path_ver = None
if os.path.exists(path_tmp):
    try:
        path_ver = os.path.join(path_dir, "Version", os.listdir(os.path.join(path_dir, "Version"))[0])
    except:
        print("Make sure there is a valid Minecraft Java Edition version in your Version folder!")
else:
    os.makedirs(os.path.join(path_tmp, "Version"))
    print("Generated Version directory. Add a valid version of Minecraft Java Edition to this folder!")

if os.path.exists(path_pack):
    print("There is still a prepared pack in the folder! Remove that first and then restart the program.")
elif path_ver is not None:
    print(f"Generating pack for {os.path.basename(path_ver)}...")

    print("Input a seed or leave empty for a random one")
    seed = "empty"
    while not seed.isdigit() and seed:
        seed = input()
    if seed:
        random.seed(seed)
    else:
        random.seed(random.randint(-2147483647,2147483647))

    # Initial setup
    print("Preparing Base files...")
    os.makedirs(os.path.join(path_dir, "RandomizedEverything"))

    WriteFileJson(os.path.join(path_dir, "RandomizedEverything"), "pack.mcmeta", {"pack": {"pack_format": 26,"description": "Randomized Everything by Rissoe | Seed: " + str(seed)}})

    path_mc_func = os.path.join(path_pack, "data", "minecraft", "tags", "functions")
    os.makedirs(path_mc_func)
    WriteFileJson(path_mc_func, "load.json", { "values": ["randomevery:load"]})
    WriteFileJson(path_mc_func, "tick.json", { "values": ["randomevery:tick"]})

    path_custom = os.path.join(path_pack, "data", "randomevery", "functions")
    path_recipes = os.path.join(path_pack, "data", "minecraft", "recipes")
    path_loot = os.path.join(path_pack, "data", "minecraft", "loot_tables")
    os.makedirs(path_custom)
    os.makedirs(path_recipes)
    os.makedirs(path_loot)

    print("--- Leave empty for YES, add text for NO ---")

    # Randomized DROPS
    if (not input("Randomize Drops? (All items dropped will be random): ")):
        print("Randomizing drops...")
        allitems = []
        for item in os.listdir(os.path.join(path_ver, "assets", "minecraft", "models", "item")):
            if "_" in item:
                segment = item.split("_")[-1].split(".")[0]
                if (not segment.isdigit() or "disc" in item) and (not "_trim" in item or "_template" in item) and item.split(".")[0] not in allitems and not item == "spyglass_in_hand.json"  and not item == "template_music_disc.json":
                    allitems.append(item.split(".")[0])
            elif item.split(".")[0] not in allitems and not item == "generated.json":
                allitems.append(item.split(".")[0])
        randomized = allitems.copy()
        random.shuffle(randomized)
        with open(os.path.join(path_custom, "randomdrop.mcfunction"), "w") as file:
            for item in zip(allitems, randomized):
                file.write(f"execute as @s[nbt={{Age=0s}}] store success entity @s Age short 1 run data modify entity @s[nbt={{Item:{{id:\"minecraft:{item[0]}\"}}}}] Item.id set value \"minecraft:{item[1]}\"\n")

    # Randomized LOOT
    if (not input("Randomize Loot? (All loottables will have ramdom items): ")):
        print("Randomizing loottables...")
        for root, dirs, files in os.walk(os.path.join(path_ver, "data", "minecraft", "loot_tables")):
            for item in files:
                with open(os.path.join(root, item), "r", encoding="utf-8") as file:
                    data = json.load(file)
                recursive_loot(data, allitems)
                path = os.path.relpath(root, os.path.join(path_ver, "data", "minecraft", "loot_tables"))
                os.makedirs(os.path.join(path_loot, path), exist_ok=True)
                with open(os.path.join(path_loot, path, item), "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)

    # Randomized RECIPES
    if (not input("Randomize Recipes? (All Recipes will be switched with another random recipe)")): 
        print("Randomizing recipes...")
        allitems = []
        for item in os.listdir(os.path.join(path_ver, "data", "minecraft", "recipes")):
            with open(os.path.join(path_ver, "data", "minecraft", "recipes", item), "r", encoding="utf-8") as file:
                data = json.load(file)
                if "result" in data and "item" in data["result"]:
                    allitems.append(data["result"]["item"])
                elif "result" in data:
                    allitems.append(data["result"])
        random.shuffle(allitems)
        for item in zip(os.listdir(os.path.join(path_ver, "data", "minecraft", "recipes")), allitems):
            shutil.copy(os.path.join(os.path.join(path_ver, "data", "minecraft", "recipes", item[0])), os.path.join(path_recipes, item[0]))
            with open(os.path.join(path_recipes, item[0]), "r", encoding="utf-8") as file:
                data = json.load(file)
                if "result" in data and "item" in data["result"]:
                    data["result"]["item"] = item[1]
                elif "result" in data:
                    data["result"] = item[1]
            with open(os.path.join(path_recipes, item[0]), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

    # Final setup
    print("Finalizing...")
    WriteFile(path_custom, "load.mcfunction", f"say RandomizedEverything Loaded with seed {seed}")
    WriteFile(path_custom, "tick.mcfunction", "execute as @e[type=minecraft:item, nbt={Age:0s}] unless data entity @s Thrower run function randomevery:randomdrop")
    print("Generated pack! Put it in the datapack folder of your world!")
input("Program Complete! Press Enter to continue.")