import subprocess

files = [
    "1_newTreasury.py",
    "2_oldTreasury.py",
    "3_stdValues.py",
    "4_frontendData.py",
]

while True:
    for file in files:
        subprocess.run(["python", file])

    print("Inflow data retrieved")

    break

