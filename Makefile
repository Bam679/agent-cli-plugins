.PHONY: check test lint fuzz-smoke vuln secrets plugin agents-md install-smoke references drift agent-check

GO ?= go
GOBIN := $(shell $(GO) env GOPATH)/bin
GOVULNCHECK ?= $(shell command -v govulncheck 2>/dev/null || echo $(GOBIN)/govulncheck)
SIBLINGS := apple-mail-cli apple-notes-cli apple-calendar-cli apple-reminders-cli paperless-cli

# Everything CI checks, locally.
check: test lint vuln secrets agents-md plugin

test:
	cd scaffold/go && $(GO) vet ./... && $(GO) test -race -count=1 -cover ./...

lint:
	cd scaffold/go && golangci-lint run ./...

fuzz-smoke:
	cd scaffold/go && ../repo/scripts/fuzz-smoke.sh 3000x

vuln:
	cd scaffold/go && $(GOVULNCHECK) ./...

secrets:
	gitleaks git --no-banner --redact .
	gitleaks dir --no-banner --redact .

agents-md:
	@scripts/check-agents-md.sh

plugin:
	claude plugin validate .
	claude plugin validate plugins/agent-cli --strict

# Installs the marketplace and every plugin into a throwaway Claude config dir.
install-smoke:
	@scripts/install-smoke.sh .

# Refresh the shared skill's per-tool references from sibling checkouts.
references:
	scripts/sync-references.sh

# Re-render the scaffold into sibling repos and report drift.
drift:
	@for r in $(SIBLINGS); do [ -d ../$$r/.scaffold ] && python3 scaffold/render.py --check ../$$r || true; done

agent-check: test
