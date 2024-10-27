import m5
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

# Create CPU and Memory Bus
system.cpu = O3CPU()
# Branch predictor
system.cpu.branchPred = LocalBP()

# Super scalar
system.cpu.fetchWidth = 12
system.cpu.issueWidth = 12
system.cpu.dispatchWidth = 12
system.cpu.commitWidth = 12
system.membus = SystemXBar()

# Create a simple cache (4-way set associative)
system.cpu.icache = Cache(
    size='32kB',
    assoc=4,  # 4-way set associative
    tag_latency=2,
    data_latency=2,
    response_latency=1,
    mshrs=16,
    tgts_per_mshr=4
)
system.cpu.dcache = Cache(
    size='32kB',
    assoc=4,  # 4-way set associative
    tag_latency=2,
    data_latency=2,
    response_latency=1,
    mshrs=16,
    tgts_per_mshr=4
)

# Connect caches to CPU and memory bus
system.cpu.icache.cpu_side = system.cpu.icache_port  # Ensure this is correctly defined
system.cpu.icache.mem_side = system.membus.cpu_side_ports

system.cpu.dcache.cpu_side = system.cpu.dcache_port  # Ensure this is correctly defined
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Set up interrupt controller
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create a memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


# Create a process for a simple "Hello World" application
process = Process()
# Set the command
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
binpath = os.path.join(
    thispath,
    "../",
    "tests/test-progs/hello/bin/x86/linux/hello",
)
# cmd is a list which begins with the executable (like argv)
process.cmd = [binpath]
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

system.workload = SEWorkload.init_compatible(binpath)

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
