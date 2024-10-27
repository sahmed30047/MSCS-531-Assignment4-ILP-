# config_no_branch_prediction.py

import m5
from m5.objects import *
import os

# Create the system
system = System()
system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create an in-order CPU (MinorCPU)
system.cpu = MinorCPU()

# Disable branch prediction
system.cpu.branchPred = NullBranchPredictor()

# Create the L1 instruction and data caches
icache = Cache(size='16kB', assoc=2)
dcache = Cache(size='16kB', assoc=2)

# Connect the caches to the CPU
system.cpu.icache = icache
system.cpu.dcache = dcache

# Create a memory bus
system.membus = SystemXBar()

# Connect caches to the memory bus
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Connect CPU ports to caches
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Create a memory controller
system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Set up the interrupt controller
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Set up the process to run (e.g., Dhrystone)
process = Process()
binary = 'path/to/your/dhrystone/binary'  # Replace with the actual path
process.cmd = [binary]

# Assign the workload to the CPU
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate the system
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting simulation without branch prediction...")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

