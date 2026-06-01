import subprocess
import os
from pathlib import Path

import alforria.funcoes_leitura as leitura

def solve():
    conf = leitura.ler_conf()
    project_root = Path(__file__).parent
    julia_path = project_root / ".." / "solver" / "JULIA"
    dat_path = Path(os.getcwd()) / Path(conf["path"]["DATPATH"] + ".jl")
 
    # if (not (julia_path / "Manifest.toml").exists()) or (not (julia_path / "Project.toml").exists()):
    #     subprocess.run(
    #         ["julia", str(julia_path / "scripts" / "setup_env.jl")], check=True
    #     )

    subprocess.run(
        ["julia", str(julia_path / "scripts" / "run.jl") , str(julia_path), str(dat_path)]
    )

if __name__ == "__main__":
    solve()