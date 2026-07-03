---
id: KB-0006
title: "Endpoint agent bad content update — boot-loop remediation"
service: endpoint
error_codes: [EPT-BOOT-291]
target_object_type: endpoint_host
adapted_from: "https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/"
adapted_from_note: "boot-loop remediation adapted near-verbatim from the CrowdStrike Channel File 291 published procedure into MediaCo endpoint terms; source page confirms the driver path and C-00000291*.sys filename glob, full Safe Mode boot sequence adapted from the published incident procedure"
source_licence: "public bulletin"
acl: public
stale: false
owner: "MediaCo Endpoint/IT Ops"
last_reviewed: 2026-05-14
---

# Endpoint agent bad content update — boot-loop remediation

## Symptoms

- Managed Windows endpoints crash to a bugcheck (BSOD) shortly after boot and enter a continuous restart loop, never reaching the desktop or the login screen.
- The MediaCo Endpoint console shows affected `endpoint_host` objects flapping offline/online or stuck in `Not Reporting`, with error code `EPT-BOOT-291` raised on the host record.
- Onset correlates with a recently pushed endpoint agent content channel update, not an OS patch or a hardware change.
- The faulting driver in the crash dump references the endpoint agent's channel file directory.

## Preconditions

- Host is a MediaCo-managed Windows endpoint running the endpoint agent sensor with automatic channel updates enabled.
- The bad channel file matching `C-00000291*.sys` is present under the agent driver directory `C:\Windows\System32\drivers\CrowdStrike\`.
- Operator has local Administrator credentials for the host, or a technician with physical/console (KVM/iLO) access.
- BitLocker recovery key for the host is retrievable from the MediaCo key-escrow console **before** starting, in case the recovery environment prompts for it (MediaCo-specific).

## Steps

1. In the MediaCo Endpoint console, locate the affected `endpoint_host` and confirm error code `EPT-BOOT-291`; place the host into a maintenance window so agent auto-recovery does not fight the fix (MediaCo-specific).
2. Retrieve the host's BitLocker recovery key from the MediaCo key-escrow console and have it on hand (MediaCo-specific).
3. At the console/KVM, boot the affected host into **Safe Mode** (or the Windows Recovery Environment). Interrupt boot three times to reach recovery options if the host will not stay up long enough.
4. If prompted, unlock the volume using the BitLocker recovery key retrieved in step 2.
5. Navigate to the endpoint agent driver directory: `C:\Windows\System32\drivers\CrowdStrike\`.
6. Locate the file matching the glob `C-00000291*.sys` and **delete** it. Do not delete any other channel file.
7. Reboot the host normally.
8. On the MediaCo Endpoint console, clear the maintenance flag and allow the agent to pull a known-good channel file (MediaCo-specific).

## Verification

"Green" is: the host completes a normal boot to the login screen without a bugcheck, the `endpoint_host` object in the MediaCo Endpoint console returns to `Reporting`/`Healthy`, `EPT-BOOT-291` clears from the host record, and the agent reports a channel file version **newer** than the bad `C-00000291*.sys` build. Confirm no `C-00000291*.sys` file remains under `C:\Windows\System32\drivers\CrowdStrike\`.

## Rollback

This procedure only deletes a single known-bad channel file; there is no restore-to-worse state, but capture a rollback path **before** deleting (our agent writes the rollback plan pre-execution):

1. Before deletion, copy `C-00000291*.sys` to a technician-accessible path (e.g. `C:\MediaCo-quarantine\`) so the exact bad artifact is preserved for forensics (MediaCo-specific).
2. If, after deletion and reboot, the host still boot-loops for an unrelated reason, the deletion is not the cause — do **not** restore the bad file. Re-enter Safe Mode and escalate.
3. To reverse the maintenance-window flag only (not the file change), clear/re-set it in the MediaCo Endpoint console; the file deletion itself is intentionally not reversible (MediaCo-specific).

## Owner & escalation

Owned by **MediaCo Endpoint/IT Ops**. If the host still boot-loops after `C-00000291*.sys` is removed, if the recovery environment cannot unlock the volume, or if fleet-wide numbers make per-host Safe Mode remediation impractical, escalate to the MediaCo Endpoint/IT Ops on-call to coordinate a bulk/imaged recovery and to raise the vendor channel-update incident. Do not re-enable automatic channel updates on recovered hosts until the vendor confirms a fixed channel file build is published.
