#!/usr/bin/env bash
# Portable compute benchmark for the mac-world project.
# Builds ns-3.29, installs Python 3.7 + pinned packages, then times one full cell
# (20,40 APs, BEB, seed 0, 1500 steps, --check) and, optionally, N cells in parallel.
#
# Usage (from the repo root, on Ubuntu 22.04 or similar):
#   bash tools/bench/run_bench.sh <provider-label> [--smoke] [--parallel N]
#     --smoke       tiny cell (2,3 APs, 2 s) to check the setup only
#     --parallel N  after the single run, run N seeds at once (no --check: it needs a single ns-3 process)
# Output: a hardware + timing report in bench-results/<provider>-<UTC time>.md (also printed).
# Needs: internet, ~10 GB free disk, root or sudo for apt. Never needs W&B login (offline).
set -euo pipefail

PROVIDER="${1:?usage: run_bench.sh <provider-label> [--smoke] [--parallel N]}"; shift || true
SMOKE=0; PAR=0
while [ $# -gt 0 ]; do
  case "$1" in
    --smoke) SMOKE=1 ;;
    --parallel) PAR="${2:?--parallel needs a number}"; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
  shift
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/bench-results"; mkdir -p "$OUT"
REPORT="$OUT/${PROVIDER}-${STAMP}.md"
LOGDIR="$OUT/${PROVIDER}-${STAMP}-logs"; mkdir -p "$LOGDIR"
VENV="${BENCH_VENV:-$HOME/venv37}"
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
export DEBIAN_FRONTEND=noninteractive WANDB_MODE=offline

if [ "$SMOKE" = 1 ]; then CELL="2,3"; SIMT=2; TS=50; else CELL="20,40"; SIMT=15; TS=300; fi

declare -A T
tick() { T[$1]=$SECONDS; }
elapsed() { echo $(( SECONDS - T[$1] )); }
say() { echo "[bench] $*"; }

# ---------- hardware ----------
say "hardware"
{
  echo "# Benchmark: $PROVIDER ($STAMP)"
  echo
  echo "Cell: --apStaCounts $CELL --mode beb --seed 0 --simTime $SIMT; smoke=$SMOKE; parallel=$PAR"
  echo
  echo "## Hardware"
  echo '```'
  lscpu | grep -E "Model name|^CPU\(s\)|Thread|Core|Socket|MHz|Hypervisor|L3" || true
  echo "nproc: $(nproc)"
  free -g | head -2
  df -h "$ROOT" | tail -1
  grep -E "^(PRETTY_NAME|VERSION_ID)=" /etc/os-release || true
  uname -r
  echo '```'
} | tee "$REPORT"

# ---------- system packages ----------
say "apt packages"; tick apt
$SUDO apt-get update -y >/dev/null
$SUDO apt-get install -y --no-install-recommends build-essential git curl ca-certificates bzip2 tar pkg-config \
  python3 python3-dev python-is-python3 libprotobuf-dev protobuf-compiler libzmq3-dev libxml2-dev libsqlite3-dev sqlite3 \
  software-properties-common >/dev/null
T_APT=$(elapsed apt)

# ---------- ns-3 build ----------
say "ns-3 configure + build (clean tree builds through waf --run)"; tick build
cd "$ROOT/ns-3.29"
./waf configure > "$LOGDIR/configure.log" 2>&1
./waf --run "scratch/linear-mesh/linear-mesh --dryRun=true --disableGym=true --apStaCounts=$CELL --simTime=1" > "$LOGDIR/build.log" 2>&1
T_BUILD=$(elapsed build)

# ---------- python 3.7 ----------
say "python 3.7 + pinned packages"; tick py
if [ ! -x "$VENV/bin/python" ]; then
  . /etc/os-release
  if [ "${ID:-}" = ubuntu ] && $SUDO add-apt-repository -y ppa:deadsnakes/ppa >/dev/null 2>&1 \
     && $SUDO apt-get update -y >/dev/null 2>&1 \
     && $SUDO apt-get install -y python3.7 python3.7-venv python3.7-dev >/dev/null 2>&1; then
    PYSRC=deadsnakes
    python3.7 -m venv "$VENV"
  else
    PYSRC=micromamba
    cd "$(mktemp -d)"
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
    ./bin/micromamba create -y -p "$VENV-conda" -c conda-forge python=3.7 >/dev/null
    "$VENV-conda/bin/python" -m venv "$VENV"
    cd "$ROOT/ns-3.29"
  fi
else
  PYSRC=existing
fi
"$VENV/bin/python" -m pip install --quiet "pip<24.1" "setuptools<66" wheel
# torch from the PyTorch index only; everything else from PyPI (avoids a broken mixed-index resolve)
"$VENV/bin/pip" install --quiet torch==1.13.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
"$VENV/bin/pip" install --quiet numpy==1.21.6 gym==0.26.2 wandb==0.18.7 protobuf==3.20.3 pyzmq==26.2.1 tqdm "matplotlib<3.6"
"$VENV/bin/pip" install --quiet --no-deps "$ROOT/ns-3.29/contrib/opengym/model/ns3gym"
T_PY=$(elapsed py)
PYVER="$("$VENV/bin/python" --version 2>&1)"

# ---------- single full cell ----------
say "single cell: $CELL beb seed 0 --check"; tick run1
cd "$ROOT/ns-3.29/scratch/linear-mesh"
set +e
"$VENV/bin/python" OSCAR_multi_ap_train.py --apStaCounts "$CELL" --mode beb --seed 0 --simTime "$SIMT" \
  --start_timesteps "$TS" --check > "$LOGDIR/single.log" 2>&1
RC1=$?
set -e
T_RUN1=$(elapsed run1)
RES1="$(grep -E '^RESULT:' "$LOGDIR/single.log" | tail -1 || true)"

# ---------- optional parallel phase ----------
PAR_ROWS=""
if [ "$PAR" -gt 0 ]; then
  say "parallel: $PAR seeds at once (no --check)"; tick runp
  pids=()
  for i in $(seq 1 "$PAR"); do
    (
      s=$SECONDS
      "$VENV/bin/python" OSCAR_multi_ap_train.py --apStaCounts "$CELL" --mode beb --seed "$i" --simTime "$SIMT" \
        --start_timesteps "$TS" > "$LOGDIR/par-$i.log" 2>&1
      rc=$?
      echo "$rc $((SECONDS - s))" > "$LOGDIR/par-$i.rc"
    ) &
    pids+=($!)
    sleep 3   # output directory names are timestamped to the second
  done
  wait "${pids[@]}" || true
  T_RUNP=$(elapsed runp)
  for i in $(seq 1 "$PAR"); do
    read -r rc secs < "$LOGDIR/par-$i.rc" || { rc="?"; secs="?"; }
    PAR_ROWS+="| seed $i | $secs | $rc |"$'\n'
  done
fi

# ---------- report ----------
{
  echo
  echo "## Software"
  echo "- Python: $PYVER (source: $PYSRC)"
  echo "- GCC: $(gcc --version | head -1)"
  echo "- protoc: $(protoc --version)"
  echo "- libzmq3-dev: $(dpkg -s libzmq3-dev | awk '/^Version/{print $2}')"
  echo "- torch: $("$VENV/bin/python" -c 'import torch;print(torch.__version__)' 2>/dev/null)"
  echo
  echo "## Timings (seconds)"
  echo "| Step | Seconds |"
  echo "|---|---|"
  echo "| apt packages | $T_APT |"
  echo "| ns-3 configure + clean build + 1 s dry run | $T_BUILD |"
  echo "| Python 3.7 + pins | $T_PY |"
  echo "| Single cell ($CELL beb seed 0 --check) | $T_RUN1 |"
  echo
  echo "Single cell exit code: $RC1; $RES1"
  if [ "$PAR" -gt 0 ]; then
    echo
    echo "## Parallel ($PAR seeds at once, whole phase ${T_RUNP}s)"
    echo "| Run | Seconds | Exit |"
    echo "|---|---|---|"
    printf "%s" "$PAR_ROWS"
  fi
} | tee -a "$REPORT"

say "report: $REPORT"
exit "$RC1"
