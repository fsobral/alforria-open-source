import shutil
import argparse
from pathlib import Path
import sys
import re


def _auto_destination(src: Path) -> Path:
    m = re.search(r"(\d+)$", src.stem)
    if m:
        number = m.group(1)
        next_number = str(int(number) + 1).zfill(len(number))
        new_stem = src.stem[:m.start()] + next_number
        return src.with_name(new_stem + src.suffix)
    return src.with_name(src.stem + "_copy" + src.suffix)


def duplicate(src: Path, dst: Path | None) -> None:
    if not src.exists():
        print(f"Fonte não encontrada: {src}")
        sys.exit(1)
    if dst is None:
        dst = _auto_destination(src)
    elif dst.is_dir():
        dst = dst / src.name
    shutil.copy2(src, dst)
    print(f"Duplicado: {src} -> {dst}")


def _largest_file_in_dir(directory: Path, extensions: set | None = None) -> Path:
    files = [p for p in directory.rglob("*") if p.is_file()]
    if extensions:
        files = [f for f in files if f.suffix.lower() in extensions]
    if not files:
        print(f"Nenhum arquivo encontrado no diretório: {directory}")
        sys.exit(1)
    return max(files, key=lambda p: p.stat().st_size)


def _largest_files_by_extension(directory: Path, extensions: set) -> list[Path]:
    """Encontra o maior arquivo para cada extensão no diretório."""
    files = [p for p in directory.rglob("*") if p.is_file()]
    result = []
    for ext in extensions:
        matching = [f for f in files if f.suffix.lower() == ext]
        if matching:
            result.append(max(matching, key=lambda p: p.stat().st_size))
    if not result:
        print(f"Nenhum arquivo encontrado com as extensões {extensions} em {directory}")
        sys.exit(1)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Duplicar um ou mais arquivos.",
        epilog=(
            "Exemplos:\n"
            "  python duplicate.py arquivo1.txt arquivo2.jpg\n"
            "  python duplicate.py arquivo1.txt arquivo2.jpg -d C:/destino"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument(
        'source',
        nargs='+',
        help='Um ou mais arquivos de origem (ex.: arq1.txt arq2.jpg)'
    )
    p.add_argument('--destination', '-d', help='Arquivo de destino ou pasta (opcional)')
    p.add_argument('--largest', '-l', action='store_true', help='Analisa um diretório e copia o maior arquivo')
    p.add_argument('--extensions', '-e', help='Filtrar por extensões (ex.: .txt,.jpg,.png)')
    args = p.parse_args()
    
    sources = [Path(s) for s in args.source]
    dst_path = Path(args.destination) if args.destination else None
    
    extensions = None
    if args.extensions:
        extensions = set(ext.lower() for ext in args.extensions.split(','))
    
    if args.largest:
        for src_path in sources:
            if not src_path.is_dir():
                print(f"A opção --largest exige um diretório de origem: {src_path}")
                sys.exit(1)
        
        if extensions:
            # Se extensões foram especificadas, encontra o maior para cada uma
            all_files = []
            for src in sources:
                all_files.extend(_largest_files_by_extension(src, extensions))
            sources = all_files
        else:
            # Se sem extensões, encontra o maior arquivo geral
            sources = [_largest_file_in_dir(src) for src in sources]
    else:
        # Só filtra por extensão se NÃO for usar --largest
        if extensions:
            sources = [s for s in sources if s.suffix.lower() in extensions]

    if len(sources) > 1 and dst_path is not None and not dst_path.is_dir():
        print("Com múltiplos arquivos, --destination deve ser uma pasta.")
        sys.exit(1)

    for src_path in sources:
        duplicate(src_path, dst_path)