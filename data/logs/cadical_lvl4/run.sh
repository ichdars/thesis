#!/bin/sh
msg () {
  printf "c run.sh: %-20s %s\n" "$1" "$2"
}
benchmark=$1
fileNameSuffix="-pre100k"
path="/usr/local/lradisk1/Benchmarks/sat/sc2024-preprocessed/preprocessed-kissat100k/$benchmark$fileNameSuffix.cnf.xz"
exec 1>"$benchmark".log 2>"$benchmark".err
msg index "$index"
msg benchmark "$benchmark"
msg path "$path"
msg job "$SLURM_ARRAY_JOB_ID"
msg task "$SLURM_ARRAY_TASK_ID"
msg host "`hostname`"
msg cpu "`lscpu|grep 'Model name:'|sed -e 's,^Model name: *,,'`"
msg os "`uname -a`"
binary=./binary
~/bin/runlim \
  --single \
  --real-time-limit=5000 \
  --space-limit=256000 \
  "$binary" \
  -n --profile=10 \
  "$path"
msg finished "`date`"
