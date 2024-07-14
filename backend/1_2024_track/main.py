import subprocess

files = [
    "1_treasuryScan.py",
    "2_deleteAM.py",
    "3_stdValues.py",
    "4_feeType.py",
    "5_frontendData.py",
]

while True:
    for file in files:
        subprocess.run(["python", file])

    print("Inflow data retrieved")

    break

