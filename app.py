"""
RareNav - Rare Disease Navigation System
=========================================
Usage:
    python app.py              # 直接启动，localhost:5000 即是完整网站
    python app.py --port 8080  # 自定义端口
    python app.py --dev        # 开发模式：同时启动 Vite dev server（需要 npm）

环境变量（均可选，缺失时自动 Demo 模式）：
    MODEL_PATH    MedGemma 模型目录   默认见下方
    CLINVAR_PATH  ClinVar TSV 文件    默认见下方
    HPO_PATH      HPO OBO 文件        默认见下方
"""

import sys
import os
import argparse
import subprocess
import threading
import logging
from pathlib import Path

ROOT_DIR     = Path(__file__).parent.resolve()
BACKEND_DIR  = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# 把 backend/ 加入模块搜索路径
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("rarenav")

# ── 数据 / 模型默认路径 ───────────────────────────────────────────────────────
_DATA_ROOT   = Path("./model_data")
DEFAULT_MODEL    = str(_DATA_ROOT / "medgemma-4b-it")
DEFAULT_CLINVAR  = str(_DATA_ROOT / "variant_summary.txt")
DEFAULT_HPO      = str(ROOT_DIR / "data" / "hp.obo")   # HPO 需单独下载，见 README


def print_banner(port: int, dev: bool):
    print(f"""
  ██████╗  █████╗ ██████╗ ███████╗███╗   ██╗ █████╗ ██╗   ██╗
  ██╔══██╗██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██║   ██║
  ██████╔╝███████║██████╔╝█████╗  ██╔██╗ ██║███████║██║   ██║
  ██╔══██╗██╔══██║██╔══██╗██╔══╝  ██║╚██╗██║██╔══██║╚██╗ ██╔╝
  ██║  ██║██║  ██║██║  ██║███████╗██║ ╚████║██║  ██║ ╚████╔╝
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝

  Rare Disease Navigation System  |  MedGemma Impact Challenge

  Mode    : {'Development (Flask + Vite)' if dev else 'Production'}
  URL     : http://localhost:{port}
  Ctrl+C to stop
""")


def check_data_files(model_path, clinvar_path, hpo_path):
    checks = [
        ("MedGemma 4B 模型目录", model_path,
         "huggingface-cli download google/medgemma-4b-it --local-dir " + model_path),
        ("ClinVar variant_summary.txt", clinvar_path,
         "wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz && gunzip && mv"),
        ("HPO hp.obo 文件", hpo_path,
         "wget https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2024-01-11/hp.obo -P data/"),
    ]
    missing = [(d, p, c) for d, p, c in checks if not Path(p).exists()]
    if missing:
        log.warning("以下文件未找到，将以 Demo 模式运行（核心功能正常，AI 输出为预设内容）：")
        for desc, p, cmd in missing:
            log.warning(f"  ✗ {desc}")
            log.warning(f"    路径: {p}")
    else:
        log.info("✓ 所有数据文件已就绪，将以完整模式启动。")


def start_vite(port=3000):
    nm = FRONTEND_DIR / "node_modules"
    if not nm.exists():
        log.info("npm install ...")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)
    log.info(f"Vite dev server → http://localhost:{port}")
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", str(port)],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    threading.Thread(
        target=lambda: [print(f"  [vite] {l.decode().rstrip()}") for l in proc.stdout],
        daemon=True
    ).start()
    return proc


def main():
    parser = argparse.ArgumentParser(description="RareNav Launcher")
    parser.add_argument("--dev",  action="store_true", help="同时启动 Vite dev server（需要 npm）")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
    args = parser.parse_args()

    # 路径：环境变量 > 默认值
    model_path   = os.environ.get("MODEL_PATH",   DEFAULT_MODEL)
    clinvar_path = os.environ.get("CLINVAR_PATH", DEFAULT_CLINVAR)
    hpo_path     = os.environ.get("HPO_PATH",     DEFAULT_HPO)

    print_banner(args.port, args.dev)
    check_data_files(model_path, clinvar_path, hpo_path)

    vite_proc = None
    if args.dev:
        try:
            vite_proc = start_vite()
        except FileNotFoundError:
            log.warning("npm 未找到，跳过 Vite。前端使用内嵌 HTML。")

    log.info("初始化后端服务（ClinVar / HPO / MedGemma）...")
    from server import create_app
    flask_app = create_app(
        model_path=model_path,
        clinvar_path=clinvar_path,
        hpo_path=hpo_path,
    )

    try:
        log.info(f"启动 → http://0.0.0.0:{args.port}")
        flask_app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)
    finally:
        if vite_proc:
            vite_proc.terminate()


if __name__ == "__main__":
    main()
