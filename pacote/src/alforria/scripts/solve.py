import subprocess
import os
from pathlib import Path

import alforria.funcoes_leitura as leitura

def solve():
    conf = leitura.ler_conf()
    julia_project_path = Path(os.getcwd()) / Path(conf["julia"]["root"])
    dat_path = Path(os.getcwd()) / Path(conf["path"]["DATPATH"] + ".jl")

    julia_scripts_root = Path(__file__).parent / ".." / "solver" / "JULIA"

    if (not (julia_project_path / "Manifest.toml").exists()) or (not (julia_project_path / "Project.toml").exists()):
        subprocess.run(
            ["julia", str(julia_scripts_root / "scripts" / "setup_env.jl"), str(julia_project_path)], check=True
        )

    subprocess.run(
        ["julia", "-i", str(julia_scripts_root / "scripts" / "run.jl") , str(julia_project_path), str(dat_path)]
    )

if __name__ == "__main__":
    solve()