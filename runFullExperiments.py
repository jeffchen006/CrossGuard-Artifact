import subprocess
import time
import os
from tqdm import tqdm

# Configuration
PYTHON_EXEC = "python3"
TOTAL_BENCHMARKS = 41 
OUTPUT_DIR = "./artifact_evaluation/logs"

# Script Paths
# Note: Using the specific paths provided in your snippets
SCRIPT_PATH_MAIN = "./constraintPackage/functionAccess_FullyOnchainVersion.py"
SCRIPT_PATH_TRACE2INV = "./constraintPackage/functionAccess_FullyOnchainVersion_Trace2Inv.py"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Task Group 1: Pruning Variations ---
# Mapping:
# --pruneRuntimeReadOnly -> RR
# --pruneCache           -> RE
# --pruneERC20           -> ERC20
# --pruneRAW             -> RAW
tasks_main = [
    # 1. RR + RE + ERC20 + RAW + 1hour
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly --pruneCache --pruneERC20 --pruneRAW --pruneParametric2 267", f"{OUTPUT_DIR}/RR_RE_ERC20_RAW_1hour.txt"),
    
    # 2. RR + RE + ERC20 + RAW + 1day
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly --pruneCache --pruneERC20 --pruneRAW --pruneParametric2 6400", f"{OUTPUT_DIR}/RR_RE_ERC20_RAW_1day.txt"),
    
    # 3. RR + RE + ERC20 + RAW + 3days
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly --pruneCache --pruneERC20 --pruneRAW --pruneParametric2 19200", f"{OUTPUT_DIR}/RR_RE_ERC20_RAW_3days.txt"),
    
    # 4. RR + RE + ERC20 + RAW
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly --pruneCache --pruneERC20 --pruneRAW", f"{OUTPUT_DIR}/RR_RE_ERC20_RAW.txt"),
    
    # 5. RR + RE + ERC20
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly --pruneCache --pruneERC20", f"{OUTPUT_DIR}/RR_RE_ERC20.txt"),
    
    # 6. RR + RE
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly --pruneCache", f"{OUTPUT_DIR}/RR_RE.txt"),
    
    # 7. RR
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN} --pruneRuntimeReadOnly", f"{OUTPUT_DIR}/RR.txt"),
    
    # 8. No options (baseline)
    (f"{PYTHON_EXEC} {SCRIPT_PATH_MAIN}", f"{OUTPUT_DIR}/baseline.txt"), 
]

# --- Task Group 2: Trace2Inv Comparisons ---
tasks_trace = [
    (f"{PYTHON_EXEC} {SCRIPT_PATH_TRACE2INV} --pruneRuntimeReadOnly --pruneCache --pruneRAW", f"{OUTPUT_DIR}/trace2inv0_CrossGuard_woTS_compared.txt"),
    (f"{PYTHON_EXEC} {SCRIPT_PATH_TRACE2INV} --pruneRuntimeReadOnly --pruneCache --pruneRAW --pruneTraining", f"{OUTPUT_DIR}/trace2inv1_CrossGuard_wTS_compared.txt"),
]

# Combine all tasks
tasks_config = tasks_main + tasks_trace

def tail_file(filename, position):
    """Reads new lines from a file starting at 'position'."""
    new_lines = []
    current_pos = position
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            f.seek(position)
            new_lines = f.readlines()
            current_pos = f.tell()
            
    return current_pos, new_lines

def run_parallel():
    processes = []
    progress_bars = []
    file_positions = []
    
    print(f"Starting {len(tasks_config)} processes in parallel...")
    print(f"Goal: {TOTAL_BENCHMARKS} benchmarks per process.\n")
    
    # 1. Start all processes
    for cmd, log_file in tasks_config:
        f_out = open(log_file, "w") 
        
        p = subprocess.Popen(cmd.split(), stdout=f_out, stderr=subprocess.STDOUT)
        processes.append(p)
        
        # Initialize Progress Bar
        # Increased spacing to <35 to accommodate longer filenames
        pb = tqdm(total=TOTAL_BENCHMARKS, desc=f"{log_file:<35}", position=len(progress_bars), leave=True)
        progress_bars.append(pb)
        
        file_positions.append(0)

    # 2. Monitor Loop
    try:
        while True:
            all_done = True
            
            for i, p in enumerate(processes):
                if p.poll() is None:
                    all_done = False
                
                log_file = tasks_config[i][1]
                current_pos = file_positions[i]
                
                new_pos, lines = tail_file(log_file, current_pos)
                file_positions[i] = new_pos
                
                # Count "benchmark:" occurrences
                update_count = 0
                for line in lines:
                    if "benchmark:" in line:
                        update_count += 1
                
                if update_count > 0:
                    progress_bars[i].update(update_count)

            if all_done:
                break
                
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping processes...")
        for p in processes:
            p.terminate()

    # 3. Cleanup
    for pb in progress_bars:
        pb.close()
    
    print("\nAll processes finished.")

if __name__ == "__main__":
    run_parallel()
