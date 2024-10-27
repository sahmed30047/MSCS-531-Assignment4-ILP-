import os
import m5
from m5.objects import *

# Create the system
system = System()

system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

# Create CPU and Memory Bus

system.cpu = O3CPU(numThreads=2)
system.multi_thread = True


system.membus = SystemXBar()

# Create instruction and data caches
system.cpu.icache = Cache(
    size='32kB',
    assoc=4,
    tag_latency=2,
    data_latency=2,
    response_latency=1,
    mshrs=16,
    tgts_per_mshr=4
)
system.cpu.dcache = Cache(
    size='32kB',
    assoc=4,
    tag_latency=2,
    data_latency=2,
    response_latency=1,
    mshrs=16,
    tgts_per_mshr=4
)

# Connect CPU's cache ports to the caches
system.cpu.icache_port = system.cpu.icache.cpu_side  # Correctly defined connection
system.cpu.dcache_port = system.cpu.dcache.cpu_side

# Connect caches to the memory bus
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Set up interrupt controller and connect to membus
system.cpu.createInterruptController()
for i in range(len(system.cpu.interrupts)):
    system.cpu.interrupts[i].pio = system.membus.mem_side_ports
    system.cpu.interrupts[i].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[i].int_responder = system.membus.mem_side_ports

# Create a memory controller and connect to membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.master

thispath = os.path.dirname(os.path.realpath(__file__))
binpath = os.path.join(
    thispath,
    "../",
    "tests/test-progs/hello/bin/x86/linux/hello",
)
# Set up processes for SMT
process_1 = Process(pid=102, cmd = binpath)
process_2 = Process(pid=101, cmd = binpath)

# Assign processes to CPU workload
system.cpu.workload = [process_1, process_2]
system.cpu.createThreads()

# Setup SE mode workload
system.workload = SEWorkload.init_compatible(binpath)

# Set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
