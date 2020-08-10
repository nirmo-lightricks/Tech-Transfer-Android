
mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
mkdir -p /mnt/disks/sdb
mount -o discard,defaults /dev/sdb /mnt/disks/sdb
echo UUID=`sudo blkid -s UUID -o value /dev/sdb` /mnt/disks/sdb ext4 discard,defaults,nofail 0 2 | sudo tee -a /etc/fstab

export LABELS=android,gcloud
export REPO_URL="https://github.com/Lightricks/facetune-android"
export ORG_RUNNER=true
export ORG_NAME=Lightricks
export RUNNER_WORKDIR=/mnt/disks/sdb/runner_workspace
RUNNER_NAME=action-runner-template3
export ACCESS_TOKEN=`gcloud secrets versions access latest --secret="GITHUB_RUNNER_APP_TOKEN"`
bash /entrypoint.sh