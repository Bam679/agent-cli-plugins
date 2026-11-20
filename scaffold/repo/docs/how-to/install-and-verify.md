# How to install and verify a __BIN__ release

This guide shows you how to install `__BIN__` without Homebrew and check that the binary was built by this repository's release workflow. Homebrew users can skip it: `brew install Bam679/tap/__BIN__` installs the same archives, and the tap only accepts releases whose signature checks out.

You need [cosign](https://github.com/sigstore/cosign) and the GitHub CLI (`gh`) for the checks.

## Download and verify an archive

Set the version, operating system and architecture you want (__ARCHIVE_CHOICES__):

```sh
V=0.1.0 OS=__EXAMPLE_OS__ ARCH=arm64
base=https://github.com/Bam679/__REPO__/releases/download/v$V
curl -fsSLO "$base/__BIN___${V}_${OS}_${ARCH}.tar.gz"
curl -fsSLO "$base/checksums.txt"
curl -fsSLO "$base/checksums.txt.sigstore.json"
```

Check that `checksums.txt` was signed by the release workflow of this repository:

```sh
cosign verify-blob --bundle checksums.txt.sigstore.json \
  --certificate-identity-regexp '^https://github.com/Bam679/__REPO__/' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com checksums.txt
```

The last line of the output is `Verified OK`. Then check the archive against the signed checksums, and check its build provenance:

```sh
shasum -a 256 --ignore-missing -c checksums.txt
gh attestation verify "__BIN___${V}_${OS}_${ARCH}.tar.gz" --repo Bam679/__REPO__
```

If any of the three checks fails, don't install the binary, and please [report it](../../SECURITY.md).

## Install the binary

```sh
tar xzf "__BIN___${V}_${OS}_${ARCH}.tar.gz" __BIN__
install -m 755 __BIN__ ~/.local/bin/
__BIN__ version
```

Make sure `~/.local/bin` is on your `PATH`. Every archive also has an SBOM (`*.sbom.json`) that lists what went into the build.

## Build from source instead

```sh
go install github.com/Bam679/__REPO__/cmd/__BIN__@latest
```

This needs Go 1.26 or later. A source build reports its module version, but it has no signature or provenance of its own.
