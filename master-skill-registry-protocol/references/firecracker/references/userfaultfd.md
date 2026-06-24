**# Firecracker Userfaultfd Handler Implementation**

**Version:** 1.0 (Firecracker main branch as of April 2026)  
**Status:** Production-ready for advanced snapshot restore / cloning use cases  
**Purpose:** Deep dive into implementing a custom **userfaultfd (Uffd)** page-fault handler for Firecracker snapshot loading. This is the advanced memory backend that gives you full control over on-demand page loading, memory sharing for clones, custom pre-warming, decompression, remote fetching, etc.

This section builds directly on the snapshotting architecture (see previous SKILL.md section). All information is taken verbatim from official Firecracker documentation (`docs/snapshotting/handling-page-faults-on-snapshot-resume.md` and `src/firecracker/examples/uffd/on_demand_handler.rs`).

## 1. Why Use a Userfaultfd Handler?

When restoring from a snapshot, Firecracker can load guest memory in two ways:

| Backend     | Handled by          | Pros                              | Cons / Use Case                     |
|-------------|---------------------|-----------------------------------|-------------------------------------|
| **File** (default) | Host kernel        | Zero code, simple                 | No custom logic, full kernel involvement |
| **Uffd**    | User-space process | Full control, on-demand, sharing, pre-warming, compression, remote pages | Requires writing/maintaining a handler process |

**Uffd** is ideal for:
- High-density cloning (share base memory file via CoW)
- Lazy loading / cold-start optimization
- Custom memory sources (e.g., compressed snapshots, network-backed pages)
- Fine-grained balloon device integration

## 2. Architecture & Interaction Flow

Firecracker and the handler communicate via a **Unix domain socket (UDS)**. The flow is strictly defined:

1. Handler binds and listens on a UDS.
2. You issue `PUT /snapshot/load` with `mem_backend.backend_type = "Uffd"` and the socket path.
3. Firecracker:
   - Creates the UFFD object
   - Privately mmaps the guest memory file (CoW)
   - Registers memory regions with UFFD
   - Connects to your UDS
   - Sends the UFFD file descriptor + memory layout (regions + page sizes) over the socket
4. Handler:
   - Receives UFFD FD and layout
   - Privately mmaps the memory file
   - Enters event loop: reads `uffd_msg` events and serves them with `UFFDIO_COPY` (or zero pages for removes)
5. No further communication on the UDS after hand-off. Firecracker waits on page faults; handler serves them.

**Visual flow summary** (from official docs):
- Handler listens on UDS → Firecracker connects and hands over UFFD + layout → Handler mmaps file privately → Page faults are served in user space.

**Jailer requirement**: The handler binary, UDS socket, and memory file **must all live inside the jail**. The UDS must be accessible only to Firecracker and the handler.

## 3. Kernel Requirements

- **5.10+**: Create UFFD via `userfaultfd(2)` syscall.
- **6.1+ (recommended)**: `/dev/userfaultfd` device (preferred). Jailer automatically exposes it inside the jail with correct permissions.
  - Without Jailer: `sudo setfacl -m u:${USER}:rw /dev/userfaultfd`

## 4. Snapshot/Load API Configuration (Uffd Backend)

```json
{
  "snapshot_path": "./snapshot.vmstate",
  "mem_backend": {
    "backend_type": "Uffd",
    "backend_path": "/path/to/uffd-socket.sock"
  }
  // ... other fields (network_overrides, etc.)
}
```

(Old deprecated `mem_file_path` is mutually exclusive.)

## 5. What Your Handler Must Implement

The handler is responsible for:
- Binding/listening on the UDS.
- Accepting Firecracker’s connection.
- Receiving the UFFD FD + memory layout over the socket.
- Privately mmap’ing the backing memory file.
- Looping on `read()` of UFFD events.
- Serving:
  - `UFFD_EVENT_PAGEFAULT` → `UFFDIO_COPY` (copy page from file)
  - `UFFD_EVENT_REMOVE` (balloon) → unregister + zero the range
- Handling errors, panics, and timeouts gracefully.
- Monitoring Firecracker’s PID via `SO_PEERCRED` (optional).

**Critical**: If the handler crashes, Firecracker **hangs forever** on the next page fault. Implement monitoring/recycling.

## 6. Official Example Implementation (Full Source)

Firecracker ships a complete, production-oriented example in Rust:

```rust
// Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

//! Provides functionality for a userspace page fault handler
//! which loads the whole region from the backing memory file
//! when a page fault occurs.

mod uffd_utils;  // (helper crate in the same directory)

use std::fs::File;
use std::os::unix::net::UnixListener;

use uffd_utils::{Runtime, UffdHandler};

fn main() {
    let mut args = std::env::args();
    let uffd_sock_path = args.nth(1).expect("No socket path given");
    let mem_file_path = args.next().expect("No memory file given");

    let file = File::open(mem_file_path).expect("Cannot open memfile");

    // Get Uffd from UDS.
    let listener = UnixListener::bind(uffd_sock_path).expect("Cannot bind to socket path");
    let (stream, _) = listener.accept().expect("Cannot listen on UDS socket");

    let mut runtime = Runtime::new(stream, file);
    runtime.install_panic_hook();
    runtime.run(|uffd_handler: &mut UffdHandler| {
        // !DISCLAIMER! (full balloon + ordering complexity explained in the code)
        let mut deferred_events = Vec::new();

        loop {
            let mut events_to_handle = Vec::from_iter(deferred_events.drain(..));

            // Read all events from the userfaultfd.
            while let Some(event) = uffd_handler.read_event().expect("Failed to read uffd_msg") {
                events_to_handle.push(event);
            }

            for event in events_to_handle.drain(..) {
                match event {
                    userfaultfd::Event::Pagefault { addr, .. } => {
                        if !uffd_handler.serve_pf(addr.cast(), uffd_handler.page_size) {
                            deferred_events.push(event);
                        }
                    }
                    userfaultfd::Event::Remove { start, end } => {
                        uffd_handler.unregister_range(start, end)
                    }
                    _ => panic!("Unexpected event on userfaultfd"),
                }
            }

            if deferred_events.is_empty() {
                break;
            }
        }
    });
}
```

**Key points from the example**:
- Loads entire region on first fault (simple greedy strategy).
- Handles `UFFD_EVENT_REMOVE` for balloon device (must zero pages).
- Defers events when `remove` blocks other ioctls (EAGAIN behavior).
- Uses a helper module `uffd_utils` (available in the same repo directory).

You can build and run this example directly from the Firecracker source tree.

## 7. Balloon Device Interaction (UFFD_EVENT_REMOVE)

The balloon device sends `MADV_DONTNEED` → Firecracker triggers `UFFD_EVENT_REMOVE`.

**Handler requirements**:
- Detect `UFFD_EVENT_REMOVE { start, end }`
- Call `unregister_range` (or equivalent)
- Zero the removed pages (so future faults return zero pages, not snapshot data)
- Production handlers must handle out-of-order events and races between `remove` and `pagefault`.

Firecracker recommends cgroup limits on the handler/Firecracker to mitigate DoS from malicious ballooning.

## 8. Best Practices & Production Considerations

- **Always run inside Jailer** (handler, UDS, mem file co-located).
- Add timeouts on UDS accept and data receive.
- Fetch Firecracker PID via `SO_PEERCRED` and monitor it.
- Install panic hooks / signal handlers to cleanly exit and notify.
- For clones: Combine with `network_overrides` and VMGenID.
- Security: Make UDS permissions 0600; memory file immutable after snapshot.
- Performance: Serve whole regions (like the example) or single pages; profile your workload.
- Monitoring: Expose metrics (pages served, latency) from the handler.
- Testing: Use the official example first, then customize (compression, remote fetch, pre-warming).
- Error handling: Never let the handler crash silently — Firecracker will hang.

**Caveats** (official):
- Handler crash → Firecracker hangs on next fault.
- UFFD queue can be blocked by pending `remove` events.
- Events may arrive out-of-order (balloon vs. vCPU threads).
- `/dev/userfaultfd` (6.1+) is strongly preferred over syscall.

## 9. Resources

- Official doc: `docs/snapshotting/handling-page-faults-on-snapshot-resume.md`
- Full example: `src/firecracker/examples/uffd/on_demand_handler.rs` + `uffd_utils`
- Snapshot load API: `docs/api_requests.md` + `snapshot-support.md`
- Ballooning: `docs/ballooning.md`
- Huge pages integration: `docs/hugepages.md`

**Pro tip**: Start with the official Rust example, containerize the handler, and run it as a sidecar inside the jail. This pattern is used in production-scale cloning and serverless platforms.

This completes the advanced snapshotting toolkit. Combine Jailer + Uffd + proper RNG/network handling for true high-density, low-latency microVM cloning. 🔥

(Keep this section synced with `CHANGELOG.md` and test against your target kernel.)