to run data collection pipeline please type (for example):

    ./docker.sh ./run_data_collection.sh --indir=/data/arxiv/src --outdir=/data/arxiv/output --pdfdir=/data/arxiv/pdf --rescale-factor=0.5 --dump-pages --nproc=2 --logfile=/data/arxiv/logfile

There are several other options, please see the `run_data_collection.sh` for complete listing.

If you make changes to the scripts used in data collection, you need to re-make the docker container:
    
    make

This may take a little time.
