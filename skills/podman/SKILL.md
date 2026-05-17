---
name: podman
description: Podman is a daemonless, rootless OCI container engine for managing containers, images, volumes, and pods. It is fully compatible with Docker CLI commands and the Docker API while offering superior security (no root daemon) and flexibility.
version: "1.0"
---

## 1. What is Podman?
- Runs on Linux natively; supports macOS and Windows via `podman machine` (VM-based remote client).
- Built on the `libpod` library.
- Supports OCI and Docker image formats.
- Full lifecycle management: build, run, checkpoint/restore (CRIU), network, pods, etc.
- No background daemon → improved security and lower idle resource usage.
- REST API with Docker-compatible + enhanced endpoints.
- Excellent Docker compatibility (drop-in replacement for most `docker` commands).

**Official Project Links (always cross-reference):**
- Main Repository: https://github.com/containers/podman
- Website: https://podman.io
- Rendered Documentation: https://docs.podman.io / https://podman.readthedocs.io

## 2. Key Features & Advantages (vs Docker)
- **Rootless by default** (no sudo required for most operations).
- **Daemonless** architecture.
- **Pods** (groups of containers sharing network/IPC namespaces, inspired by Kubernetes).
- Native **Kubernetes YAML** support (`podman kube play/generate`).
- **Quadlet** (systemd-native container management via `.container`/`.pod`/`.image`/`.volume` unit files).
- **Netavark** (modern networking stack).
- **Image signing & trust** policies.
- **Machine** management for remote clients (macOS/Windows).
- **Farm** (multi-host build farms).
- **Artifact** commands (new in recent versions for handling OCI artifacts).
- Full compatibility with Docker CLI + API.
- Built-in **remote client** support.

## 3. Documentation References (MANDATORY – Always Link These)

### Core Documentation Tree (GitHub)
- **Main Docs Directory:** https://github.com/containers/podman/tree/main/docs
- **Full README:** https://github.com/containers/podman/blob/main/docs/README.md
- **Manpage Syntax Guide:** https://github.com/containers/podman/blob/main/docs/MANPAGE_SYNTAX.md
- **Kubernetes Support:** https://github.com/containers/podman/blob/main/docs/kubernetes_support.md
- **Code Structure:** https://github.com/containers/podman/blob/main/docs/CODE_STRUCTURE.md

### Command Documentation (Markdown Source – All Man Pages)
https://github.com/containers/podman/tree/main/docs/source/markdown

**categorized List of Command Markdown Files:**

#### Artifact Commands
- [podman-artifact.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact.1.md)
- [podman-artifact-add.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-add.1.md.in)
- [podman-artifact-extract.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-extract.1.md)
- [podman-artifact-inspect.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-inspect.1.md)
- [podman-artifact-ls.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-ls.1.md.in)
- [podman-artifact-pull.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-pull.1.md.in)
- [podman-artifact-push.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-push.1.md.in)
- [podman-artifact-rm.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-artifact-rm.1.md)

#### Container Commands
- [podman-container.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container.1.md)
- [podman-attach.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-attach.1.md.in)
- [podman-container-checkpoint.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-checkpoint.1.md)
- [podman-container-cleanup.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-cleanup.1.md)
- [podman-container-clone.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-clone.1.md.in)
- [podman-container-diff.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-diff.1.md.in)
- [podman-container-exists.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-exists.1.md)
- [podman-container-inspect.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-inspect.1.md.in)
- [podman-container-prune.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-prune.1.md)
- [podman-container-restore.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-restore.1.md)
- [podman-container-runlabel.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container-runlabel.1.md.in)
- [podman-container.unit.5.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-container.unit.5.md.in)

#### Image Commands
- [podman-image.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-image.1.md)
- [podman-build.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-build.1.md.in)
- [podman-commit.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-commit.1.md)
- [podman-images.1.md.in](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-images.1.md.in)
- [podman-import.1.md](https://github.com/containers/podman/blob/main/docs/source/markdown/podman-import.1.md)
- (Full list of image-related files: `podman-image-diff`, `podman-image-exists`, `podman-image-inspect`, `podman-image-mount`, `podman-image-prune`, `podman-image-scp`, `podman-image-sign`, `podman-image-tree`, `podman-image-trust`, `podman-image-unmount`, `podman-image.unit.5.md.in`, etc. – see directory)

#### System, Machine, Farm & Misc Commands
- `podman-machine.*`, `podman-farm.*`, `podman-info`, `podman-events`, `podman-logs`, `podman-exec`, `podman-create`, `podman-run`, `podman-start/stop/rm`, `podman-ps`, `podman-inspect`, `podman-kill`, `podman-logs`, `podman-cp`, `podman-diff`, `podman-export/import`, `podman-load/save`, `podman-login/logout`, `podman-auto-update`, `podman-completion`, `podman-generate-*`, `podman-healthcheck`, `podman-history`, `podman-init`, `podman-mount/unmount`, etc.
- **Full directory (ALL files):** https://github.com/containers/podman/tree/main/docs/source/markdown

**Shared Options (included via @@option in man pages):**  
https://github.com/containers/podman/tree/main/docs/source/markdown/options (e.g., `env.md`, `volume.md`, `network.md`, `cap-add.md`, etc.)

**Aliases/Links:** https://github.com/containers/podman/tree/main/docs/source/markdown/links

### Tutorials & Advanced Guides
**Tutorials Directory:** https://github.com/containers/podman/tree/main/docs/tutorials
- `podman_tutorial.md`, `rootless_tutorial.md`, `basic_networking.md`, `image_signing.md`, `remote_client.md`, `mac_client.md`, `podman-for-windows.md`, `performance.md`, `socket_activation.md`, `qemu-remote-tutorial.md`, `podman-derivative-api.md`, etc.

**CNCF Self-Assessment:** https://github.com/containers/podman/tree/main/docs/cncf/self-assessment.md

**Build & Rendering:** See `docs/README.md` for `make docs`, `make html`, Sphinx, Pandoc, etc.

## 4. Core Workflows & Common Commands (Agent Must Master)
**Always prefer official man pages for exact syntax/flags.**

- **Build:** `podman build -t image:tag .` (or `podman buildx` compatibility)
- **Run:** `podman run -d --name mycont -p 8080:80 image`
- **Pods:** `podman pod create`, `podman pod run`
- **Kube:** `podman kube play deployment.yaml`, `podman kube generate`
- **Rootless:** No special flags needed in most modern installs
- **Machine (macOS/Windows):** `podman machine init/start/ssh`
- **Quadlet:** Place `.container` files in `~/.config/containers/systemd/` or `/etc/containers/systemd/`
- **Remote:** `podman --remote` or set `CONTAINER_HOST`

**Manpage Syntax Reminder:** Follow exact formatting from `MANPAGE_SYNTAX.md` (OPTIONS in alphabetical order, bold defaults, tables for complex args, no pronouns, etc.).

## 5. Best Practices & Advanced Topics (Agent Guidance)
- Prefer **rootless** mode.
- Use **pods** for multi-container apps.
- Leverage **Quadlet** for systemd integration, use SKILL `podman-quadlet` when you need to deal with quadlet.
- Use **Netavark** + CNI plugins for complex networking.
- Enable **image signing** with `podman image trust`.
- Use `podman farm` for distributed builds.
- Monitor with `podman events`, `podman system df`, `podman info`.
- Security: Use `--security-opt`, capabilities, seccomp, apparmor/selinux.
- Volumes: Named volumes preferred over bind mounts for portability.
- Always check `podman version` and `podman info` for configuration.

## 6. Docker Compatibility & Migration
- Most `docker` commands work with `podman` (alias `docker=podman`).
- Differences: No daemon, rootless by default, pod concept, different storage/network drivers.
- See official migration guides in rendered docs.

## 7. Troubleshooting & Common Issues
- Rootless networking/permission issues → check `containers.conf`.
- Remote connection → `podman system connection`.
- Build cache → `podman builder prune`.
- Always reference `podman --help` + specific man page.

## 8. Agent Usage Instructions
- **Always cite the exact GitHub Markdown file** or rendered ReadTheDocs page when answering.
- Provide complete command examples with common options (e.g., `--rm`, `-v`, `--name`, `--network`, `--env`).
- For complex tasks, combine commands (e.g., `podman build && podman run` or Quadlet units).
- Recommend reading the full man page for any command.
- Stay up-to-date: Check the `main` branch of https://github.com/containers/podman/tree/main/docs/source/markdown for latest command docs.


**Associated SKILLs:**
- `podman-quadlet`