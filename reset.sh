cp Data/backup.json Data/tree.json

rm file/*
echo "{}" > file/chunk_refs.json

rm VirtualDisk/pi{1,2,3}/*
echo "{}" > VirtualDisk/pi1/chunk_refs.json
echo "{}" > VirtualDisk/pi2/chunk_refs.json
echo "{}" > VirtualDisk/pi3/chunk_refs.json
