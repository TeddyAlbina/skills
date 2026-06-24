---
name: podman-quadlet
description: skill only for creating, managing, or troubleshooting containers or pods as systemd services using Podman Quadlet.
version: "1.0"
---

## Overview
**Podman Quadlet** is Podman’s native **systemd generator** that lets you define containers, pods, networks, volumes, images, and Kubernetes workloads using simple INI-style files.

Instead of writing complex `.service` files or using `podman generate systemd`, you drop `.container`, `.pod`, `.volume`, etc. files in the right directory and `systemctl daemon-reload` does the rest.

Quadlet turns Podman into a first-class systemd citizen:
- Automatic start on boot
- Proper restart policies, dependencies, logging
- Rootless by default (recommended)
- Built-in auto-updates (`AutoUpdate=registry`)
- Clean lifecycle management (no orphaned containers)
- Native `podman quadlet` CLI (since Podman 5.x / 2025)

## Platform Support

- **Linux**: Fully native and recommended (best performance with direct systemd integration).
- **Windows**: Not available natively on the Windows host (no systemd).  
  Quadlet works **inside** the Podman Machine (Linux VM).  
  **Recommended**: Use **Podman Desktop** + the official **Quadlet extension** (easiest GUI experience).  
  Alternative: `podman machine ssh` into the VM and manage files manually.
- **macOS**: Same as Windows — works inside the Podman Machine.

> **Note**: Quadlet is primarily a Linux technology. For production-grade .NET deployments, Linux hosts are recommended for optimal performance and support. Quadlet is not available natively on Windows or macOS hosts; use it only inside the Podman Machine or Podman Desktop with the Quadlet extension. If a user asks for native Quadlet on Windows or macOS, explain that it is supported only in a Linux VM environment.

## Supported Quadlet File Types

| Extension     | Purpose                              | Typical Use Case                          |
|---------------|--------------------------------------|-------------------------------------------|
| `.container`  | Single container                     | Web apps, APIs, workers, databases        |
| `.pod`        | Multi-container pod                  | Tightly-coupled services sharing network  |
| `.network`    | Custom Podman network                | Isolated or internal networking           |
| `.volume`     | Named volume                         | Persistent data                           |
| `.image`      | Pre-pull & manage image              | Faster starts & image pinning             |
| `.build`      | Build image from Containerfile/Dockerfile | Local .NET builds (`dotnet publish`) |
| `.kube`       | Run Kubernetes YAML                  | `podman kube play` equivalent             |

## Search Directories (in order of precedence)

**Rootless (strongly recommended):**
- `~/.config/containers/systemd/`

**System-wide (root):**
- `/run/containers/systemd/` (temporary)
- `/etc/containers/systemd/`
- `/usr/share/containers/systemd/`

Drop-in overrides go in `myapp.container.d/10-custom.conf`

## When to Use This Skill
- User wants to run any container as a systemd service
- Migrating from `podman run`, `docker-compose`, or raw systemd units
- Deploying C#/.NET apps (ASP.NET, Worker Service, etc.)
- Setting up production services with auto-restart, auto-update, volumes, secrets
- Replacing Docker Compose on Linux servers
- Managing multi-container .NET solutions (API + DB + cache)

## Core Workflow for AI Agents (Follow Every Time)

1. **Gather requirements**  
   - Single container or pod?  
   - Ports to publish?  
   - Volumes / persistent data?  
   - Environment variables / secrets?  
   - Rootless or rootful?  
   - Auto-update needed?  
   - Any dependencies (network, other services)?

2. **Choose file types** (use the smallest set possible)

3. **Generate clean, well-commented files** with:
   - `[Unit]`, `[Container]`/`[Pod]`, `[Service]`, `[Install]` sections
   - Full-qualified image names
   - Descriptive `ContainerName=`, `PodName=`
   - Proper `[Install] WantedBy=`

4. **Provide activation commands**:
   ```bash
   systemctl --user daemon-reload          # or sudo systemctl daemon-reload
   systemctl --user enable --now myapp.service
   ```

5. **Verify & debug**:
   ```bash
   systemctl --user status myapp.service
   journalctl --user -u myapp.service -f
   podman ps
   ```

6. **Offer migration help** (docker-compose → Quadlet)

## Best Practices (Always Enforce)

- Use **fully-qualified image names**
- Enable `AutoUpdate=registry` for production
- Prefer named volumes over bind mounts when possible
- Use `:Z` or `:z` on bind mounts (SELinux)
- Set `Restart=always` in `[Service]`
- Use `TimeoutStartSec=300` (or higher for .NET apps)
- Add `After=network-online.target` + `Wants=network-online.target`
- Use systemd specifiers (`%h`, `%i`, `%p`) correctly
- Keep Quadlet files in Git
- For complex apps → use one directory with multiple `.container` + `.volume` files

## Common `[Container]` Directives (most used)

- `Image=`
- `ContainerName=`
- `PublishPort=8080:80` (or `127.0.0.1:8080:80`)
- `Volume=`, `Mount=`
- `Environment=`, `EnvironmentFile=`
- `Network=`, `Pod=`
- `AutoUpdate=registry|local`
- `Exec=`, `WorkingDir=`
- `User=`, `Group=`
- `Secret=`, `Label=`
- `AddCapability=`, `DropCapability=`

(Full list is in `man podman-systemd.unit`)

## Example: C# ASP.NET Core App (rootless)

```ini
# ~/.config/containers/systemd/myapi.container
[Unit]
Description=My .NET API
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/yourorg/myapi:latest
ContainerName=myapi
PublishPort=8080:8080
Volume=myapi-data:/app/data:Z
Environment=ASPNETCORE_ENVIRONMENT=Production
Environment=DOTNET_GCHeapHardLimit=0x40000000
AutoUpdate=registry

[Service]
Restart=always
TimeoutStartSec=180

[Install]
WantedBy=default.target
```

## New Podman Quadlet CLI (Podman ≥ 5.x)

```bash
podman quadlet install myapp.container          # from file or URL
podman quadlet list
podman quadlet print myapp.container
podman quadlet rm myapp.container --all
```

## Pro Tips for .NET Developers

- Use `.build` units to build your .NET app from source on the server
- Combine `.volume` + `.container` for database + API
- Use `.pod` when your .NET service needs sidecar containers
- Store secrets via `podman secret` + `Secret=` key
- Enable auto-updates + healthchecks for zero-downtime .NET deployments

---

**This skill pairs perfectly with:**
- Docker Compose → Quadlet migration skill
- C#/.NET containerization best practices
- Systemd hardening & security skills

**Pro tip for agents:** When the user pastes a `docker run` command or `docker-compose.yml`, automatically convert it to clean Quadlet files and explain every decision. 