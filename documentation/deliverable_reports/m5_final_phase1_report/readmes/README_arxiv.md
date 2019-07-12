---
title: "ArXiv processing README"
---

# Re-creating equation dataset

1. Download the complete set of arXiv PDFs and their corresponding source files from Amazon S3 as described [here](https://arxiv.org/help/bulk_data_s3).  Our dataset contains papers up through December 2018.

2. Download docker

3. Clone the AutoMATES repo

4. Expand and normalize the directory structure

   - Expand the src files:

     - Takes 2 positional arguments: (1) directory with tarballs and (2) directory where the expanded files should go
     - Optionally use `—keepall` if you want to keep intermediate files.  We use this with the pdf directory expansion because otherwise the newly expanded pdfs would be deleted!

     cd automates/equation_extraction

     python expand_arxiv.py <path_to_arxiv_src_dir> data/arxiv/src 

   - Expand the pdf files (optional, but makes subsequent steps WAY faster!)

     `python expand_arxiv.py <path_to_arxiv_pdf_dir> data/arxiv/pdf —keepall`

4. Build the docker container for processing the LaTeX documents

   `docker build -t clulab/equations .`

5. Collect the data for the separate equation detection and decoding tasks:

   `./docker.sh ./run_data_collection.sh --indir=/data/arxiv/src --outdir=/data/arxiv/output --pdfdir=/data/arxiv/pdf --rescale-factor=0.5 --dump-pages --nproc=2 --logfile=/data/arxiv/logfile`

   Takes several arguments:

   - indir: the directory with the expanded src files
   - outdir: the directory for storing the collected training data
   - pdfdir (optional): the directory for the expanded pdf files, if using (makes it faster!)
   - rescale-factor: rescales the collected equation images, using a rescale factor of 0.5 uses far less disk space and still generates high-quality images
   - dump-pages (optional): if included, keeps individual images of each page of the pdf.  We use these for training the equation detection module.
   - nproc: the number of processess that you will run (to parallize the data collection)

   
