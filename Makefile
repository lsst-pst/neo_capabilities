LATEX       = pdflatex
BIBTEX      = bibtex
BASH        = bash -c
ECHO        = echo
RM          = rm -rf
RM_TMP      = ${RM} $(foreach suff, ${TMP_SUFFS}, ${NAME}.${suff})

TMP_SUFFS   = pdf aux bbl blg log dvi ps eps out
SUFF        = pdf

CHECK_RERUN = grep Rerun $*.log

NAME    = neo_capabilities
DOC_OUT = ${NAME}.${SUFF}

DEPENDENCIES = LSSToverview.tex appendix1.tex appendixMOPS.tex appendix_fallback_strategies.tex discussion.tex
DEPENDENCIES := image_differencing.tex intro.tex mops.tex neo_capabilities.tex opsim.tex strategy.tex

default: ${DOC_OUT}

%.pdf: %.tex %.bib $(DEPENDENCIES)
	${LATEX} $<
	( ${CHECK_RERUN} && ${LATEX} $< ) || echo "Done."
	${BIBTEX} $(<:.tex=.aux)
	${LATEX} $<
	( ${CHECK_RERUN} && ${LATEX} $< ) || echo "Done."

clean:
	${RM_TMP}
