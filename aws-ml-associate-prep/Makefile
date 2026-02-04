# Makefile for AWS ML Labs PDF generation

.PHONY: all clean help lab-%

# Default target - build combined PDF
all:
	@./scripts/build-pdf.sh all

# Build specific lab (e.g., make lab-01)
lab-%:
	@./scripts/build-pdf.sh $*

# Clean build artifacts
clean:
	@./scripts/build-pdf.sh clean

# Help
help:
	@echo "AWS ML Labs PDF Builder"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Build combined PDF of all labs"
	@echo "  make lab-01   - Build PDF for lab 01 only"
	@echo "  make lab-09   - Build PDF for lab 09 only"
	@echo "  make clean    - Remove build artifacts"
	@echo ""
	@echo "Output files are saved to ./output/"
