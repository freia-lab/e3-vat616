# e3-vat616

Wrapper for the module vat616

<!-- This README.md should be updated as part of creation and should add complementary information about the wrapped module in question (usage, etc.). Once the repository is set up, empty/unused directories should also be purged. -->

## Requirements

<!-- Put requirements here, like:
- libusb
- ...
-->

## EPICS dependencies


```sh
$ make dep
STREAM_DEP_VERSION = 2.8.18+0
require vat616,main
< configured ...
```


## Installation

```sh
$ make init patch build
$ make install
```

For further targets, type `make`.

## Usage

```sh
$ iocsh.bash -r "vat616"
```

## Additional information

<!-- Put design info or links (where the real pages could be in e.g. `docs/design.md`, `docs/usage.md`) to design info here.
-->

## Contributing

Contributions through pull/merge requests only.
