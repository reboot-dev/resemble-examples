# Resemble Examples

<!--
TODO: include a frontend in this example.
-->

This repository contains example applications written using Resemble. The
examples are structured in the style of a monorepo: all proto files can be found
in the `api/` directory, grouped into subdirectories by proto package, while application code is broken into top-level directories by
application name.

For example, the `hello-world` application uses code from `hello-world/` and
protos from `api/hello-world/`.

## Setup

You can run this example in the following ways:

### On a GitHub Codespace

GitHub's Codespaces are [Dev Containers](https://containers.dev/) running on
cloud machines.

To try these examples in a Codespace:

1. Fork this repository, so that it is owned by your own GitHub account.
2. In GitHub's webinterface, click the green "<>" (AKA "Clone, Open, or
   Download") button.
3. Select the "Codespaces" tab
4. Click the "+" button.

This will open a cloud-hosted VSCode editor, with all of the necessary tools
installed, and with the repository's code already checked out.

### In a local Dev Container

[Dev Containers](https://containers.dev/) are a convenient way to create
reproducible development environments. Resemble provides a Dev Container that
mimics the Resemble production environment; if your application works in the Dev
Container, it will work in production.

The GitHub Codespaces discussed above are Dev Containers that run in the cloud.
You can also choose to run the same Dev Container locally, on your own machine.
Your filesystem will be mounted into the Dev Container, so you can develop as
normal, just within the predictable environment of a Docker container.

> [!IMPORTANT]
> Currently, the Resemble Dev Container only works on x86 CPU architectures.
> **Apple-silicon (M1/M2/...) Mac users**: we will be providing support for your
> machines soon!

Start by cloning this repository:

<!-- TODO: fetch this snippet from a test. -->

```shell
git clone https://github.com/reboot-dev/resemble-examples.git
cd resemble-examples/
```

> [!NOTE]
> The Dev Container's configuration is found in
> `.devcontainer/devcontainer.json`. You may expand on it to customize your
> development environment to your liking.

How you access the Dev Container will likely depend on the editor/IDE you prefer.

#### Using VSCode

VSCode has built-in support for Dev Containers. Open your Dev Container as follows:

- In VSCode, open the `resemble-examples` folder you've cloned.
- Press: Ctrl+Shift+P (Linux / Windows) or Command+Shift+P (Mac)
- Type/Select: `Dev Containers: Reopen In Container`

VSCode will now start your dev container, and restart VSCode to be running
inside of that container.

#### Using a non-Dev-Container-aware editor

If your editor does not have built-in support for Dev Containers, you can use the `devcontainer` CLI.

Install the CLI as follows:

```
npm install -g @devcontainers/cli
```

Then start the Dev Container, and `exec` into it:

```
devcontainer up --workspace-folder .
devcontainer exec /bin/bash
```

### Without using a Dev Container

> [!IMPORTANT]
> Currently, Resemble backends can only run on x86 Linux machines with
> `glibc>=2.35` (Ubuntu Jammy and other equivalent-generation Linux
> distributions). If you have a machine that doesn't fit this requirement, we
> suggest using one of the Dev Container approaches discussed above.

Start by cloning this repository:

<!-- TODO: fetch this snippet from a test. -->

```shell
git clone https://github.com/reboot-dev/resemble-examples.git
cd resemble-examples/
```

<!-- TODO: Update the Quick Start link below once the Resemble docs are published with a more official address. -->

Next, follow the [Installation
section](https://vigilant-adventure-g31v411.pages.github.io/docs/quick-start#installation)
of the Resemble "Quick Start" guide to set up general Resemble requirements.

## Run an Example

These steps will walk you through the process of downloading and running
examples from this repository locally on your machine.

### Install Python Requirements

As with most Python applications, these examples have requirements that must be
installed before the application code can run successfully. These Python
requirements include the Resemble backend library, `reboot-resemble`.

Requirements are specific to a particular example application. The following
command will install requirements for the `HelloWorld` application.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=52-52) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pip install -r hello-world/backend/src/requirements.txt
```
<!-- MARKDOWN-AUTO-DOCS:END -->

### Compile Protocol Buffers

Run the Resemble `protoc` plugin to generate Resemble code based on the protobuf
definition of a service. The following command will generate code for the
`HelloWorld` application, whose sole service is defined in `greeter.proto`:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=55-55) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
rsm protoc ./api/hello_world/v1/greeter.proto
```
<!-- MARKDOWN-AUTO-DOCS:END -->

The `rsm` tool will automatically pull in required Resemble proto dependencies
like `resemble/v1alpha1/options.proto`, even though they're not found in this
repository.

<!-- TODO: link to the Resemble proto definitions once they are publicly available. -->

## Test

The example code comes with example tests. To run the example tests, use `pytest`:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./readme_test.sh&lines=58-58) -->
<!-- The below code snippet is automatically added from ./readme_test.sh -->
```sh
pytest hello-world/backend/
```
<!-- MARKDOWN-AUTO-DOCS:END -->

## Run

To start an application, use the `rsm` CLI. The following command starts the
`HelloWorld` example.

<!--
TODO: include this command in readme_test.sh.
-->

<!--
TODO(benh,zakhar): auto-detect the PROTOPATH.
TODO(rjh): add appropriate `--watch`es. It seems they may not work as desired right now?
-->

```shell
PYTHONPATH="gen/:hello-world/backend/src" rsm dev --working-directory=. --python hello-world/backend/src/main.py
```

The PYTHONPATH must be explicitly set to pick up both the generated Resemble
code and the application code.

`rsm dev` will then run the Python script specified by the
`--python` flag from the directory specified by the `--working-directory` flag.

The tool will automatically watch the given python script for changes. If there
are changes, it will restart the running application to reflect the update.

<!--
TODO: introduce an `rsm grpcurl` (or `rsm call` or ...) that lets us explore
our backend in another terminal by calling RPCs.
-->
