NAME=main
OUTDIR=build

default: $(NAME).pdf

$(NAME).pdf: $(NAME).tex $(NAME).bib
	latexmk -outdir=$(OUTDIR) -pdf $(NAME).tex

.PHONY: clean
clean:
	@rm -rf $(OUTDIR)
