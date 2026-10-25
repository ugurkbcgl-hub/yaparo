# ADR-0050: Bounded unsaved editor undo/redo

- Status: Accepted for local synthetic implementation
- Date: 2026-10-25
- Continues Y06 and ADR-0042/0048/0049.

Add client-memory-only Geri al/Yinele buttons for up to50 accepted editing steps.
Each changed valid input event or completed Fabric transform records the prior
scene. No-op/invalid inputs and selection changes add no step. New edits discard
the redo branch; snapshots contain only scene values, not image bytes or URLs.
This does not call a provider, write localStorage or send an undo/redo request.

Applying a step updates the existing objects and control panel without image
reload. Fabric modified handlers resolve the current scene by stable layer ID,
so dragging after undo cannot mutate a stale captured scene. Pointer gestures,
pending save/restore and unready rendering disable history actions. Schema,
material/version binding and scene validation remain unchanged for v1–v3.

Ctrl/Cmd+Z, Ctrl+Y and Ctrl/Cmd+Shift+Z operate outside editable inputs. Native
input/textarea/select/contenteditable behavior is left intact. The preview is
keyboard-focusable, buttons have shortcut labels and mobile actions wrap in a
two-column layout. Accepted keystroke input events may be separate steps; typing
burst grouping is not implemented.

Dirty state compares the current scene with the last loaded/accepted saved scene.
Successful save clears both local stacks and establishes the submitted snapshot
as baseline. Successful committed-history restore/render resets local steps and
initializes the title controls directly even while the request guard is active.
Failed save/restore preserves current edits and stacks; no automatic retry.
Reload closes this in-memory history; immutable server save/restore history is
separate. The UI explains these limits. This is not cross-tab history or offline
draft persistence.

Verification uses real Chromium controls/shortcuts, native-field event behavior,
50-step cap/no-op/branch semantics, no network writes for local actions, pending
and failed save, successful save/reload/restore, color changes and real pointer
drag-after-undo with legacy v1 and palette v3. A review-found restore panel
mismatch was fixed and covered with hero-selected restore followed by title edit.
Desktop/mobile screenshots reviewed. No model, migration, provider or data reset.

Next: separately versioned square/portrait design selection and PNG export while
preserving existing v1–v3 appearance, bindings, local undo and committed history.
