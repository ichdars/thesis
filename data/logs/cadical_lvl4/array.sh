#!/bin/sh
#SBATCH --job-name=223.0.0-0i0
#SBATCH --array=1-7
#SBATCH --partition=cpu-single
#SBATCH --nodes=1
#SBATCH --sockets-per-node=2
#SBATCH --cores-per-socket=32
#SBATCH --time=5002
#SBATCH --mem=256G
delta=64
msg () {
  printf "c array.sh: %-20s %s\n" "$1" "$2"
}
msg job "$SLURM_ARRAY_JOB_ID"
msg task "$SLURM_ARRAY_TASK_ID"
end=`expr $SLURM_ARRAY_TASK_ID \* $delta + 1`
start=`expr $end - $delta`
limit=`expr  + 1`
[ $end -gt $limit ] && end=$limit
msg start $start
msg end $end
index=$start
while [ $index -lt $end ]
do
  msg index $index
  benchmark=`awk '$1 == '$index' { print $2 }' benchmarks`
  msg benchmark "$benchmark"
  ./run.sh $index &
  index=`expr $index + 1`
done
wait
msg done "`date`"
