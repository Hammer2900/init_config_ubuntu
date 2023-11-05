#!/bin/bash

DEFAULT_URL="/home/izot/Downloads/nixos-minimal-23.05.4662.34bdaaf1f0b7-x86_64-linux.iso"
DEFAULT_DISC="nixos-hdd.qcow2"

START_TEMPLATE=(
  "-enable-kvm"
  "-smp 6"
  "-m 7096"
  "-boot d"
  "-cdrom ${DEFAULT_URL}"
  "-hda ${DEFAULT_DISC}"
#  "-netdev bridge,br=br-25f81bb8d6cc,id=net0"
#  "-device virtio-net-pci,netdev=net0"
)

run_vm() {
  echo "Creation of the new VM..."
  if [ ! -f $DEFAULT_DISC ]; then
    echo "Disk ${DEFAULT_DISC} does not exist. Creating..."
    qemu-img create -f qcow2 $DEFAULT_DISC 60G
  fi
  echo "Running the VM..."
  qemu-system-x86_64 ${START_TEMPLATE[@]}
}

clean() {
  echo "Starting clean up process..."
  kill_vm

  if [ -e $DEFAULT_DISC ];
  then
    echo "$DEFAULT_DISC exists; Deleting..."
    rm $DEFAULT_DISC
    echo "Disk file $DEFAULT_DISC deleted."
  else
    echo "$DEFAULT_DISC does not exist; No action taken."
  fi

  echo "Clean up process completed."
}

kill_vm() {
  echo "Attempting to kill the qemu process..."
  PIDS=$(ps -ef | grep qemu-system-x86_64 | grep -v grep | awk '{print $2}')
  if [ -z "$PIDS" ]; then
    echo "No running qemu process found."
  else
    for PID in $PIDS; do
      echo "Killing qemu process with pid: $PID"
      kill $PID
    done
    echo "Successfully killed the qemu process."
  fi
}

info() {
  if [ -e $DEFAULT_DISC ];
  then
    echo "$DEFAULT_DISC exists."
    echo "Size: $(du -sh $DEFAULT_DISC | cut -f1)"
    echo "Created: $(date -r $DEFAULT_DISC)"
  else
    echo "$DEFAULT_DISC does not exist."
  fi
}

echo "VM manager v1.0"

run_vm
#clean
#kill_vm
#info