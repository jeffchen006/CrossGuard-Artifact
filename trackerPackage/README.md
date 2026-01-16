# trackerPackage

These modules track EVM state as traces are replayed. They are used by the analysis pipeline to understand how memory, stack, and storage change across execution.

## What these trackers cover

- `memoryTracker.py`: tracks memory reads/writes.
- `stackTracker.py`: tracks stack state across opcodes.
- `storageTracker.py`: tracks storage access and updates.
- `dataSource.py`: common interface for feeding trace data to trackers.
- `tracker.py`: orchestrates the trackers so they work together.

## How it fits in the pipeline

- The trace parsers call into these trackers to build higher-level features.
- The outputs flow into the invariant discovery and analysis steps.

## Notes

- These modules are performance-sensitive. Small changes here can have large runtime impact.
- If you are debugging a trace mismatch, this is a good place to add temporary logging.
