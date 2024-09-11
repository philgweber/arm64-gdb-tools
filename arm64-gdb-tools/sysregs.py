import gdb
import openocd

# https://developer.arm.com/documentation/ddi0595/2020-12/AArch64-Registers
#   "REG Name" : (ELx,op0,op1,CRn,CRm,op2)
sysregs = {
    "CNTPCT_EL0":   (0,3,3,14,0,1),
    "TTBR0_EL1" :   (1,3,0,2,0,0),
    "MAIR_EL1"  :   (1,3,0,10,2,0),
    "SCTLR_EL1" :   (1,3,0,1,0,0),
    "ESR_EL1"   :   (1,3,0,5,2,0),
    "ESR_EL2"   :   (2,3,4,5,2,0),
    "ELR_EL1"   :   (1,3,0,4,0,1),
    "ELR_EL2"   :   (2,3,4,4,0,1),
    "FAR_EL1"   :   (1,3,0,6,0,0),
    "FAR_EL2"   :   (2,3,4,6,0,0),
#    "ICC_CTLR_EL1" :   (1,3,0,12,12,4),
    "DAIF"      :   (1,3,3,4,2,1),
}


class Sysregs(gdb.Command):
    """Print system registers"""

    def __init__ (self):
        super (Sysregs, self).__init__ ("sysregs", gdb.COMMAND_USER)
        self.ocd = openocd.OpenOcd()
        self.ocd.connect()
        gdb.events.exited.connect(self.ocd_disconnect)
    
    def ocd_disconnect(self):
        self.ocd.disconnect()

    def invoke(self, arg, from_tty):
        # By default assume EL1 if we can't get it
        current_el = 1
        # MRS command to read current EL 3,0,4,2,2
        el = self.ocd._mrs(3,0,4,2,2)
        current_el = int(el,16) >> 2 
        print("Current EL: " + str(current_el))
        for reg in sysregs:
            # Only try to print the register if at acceptable EL
            if(current_el >= sysregs[reg][0]):
              out = self.ocd._mrs(sysregs[reg][1], sysregs[reg][2], sysregs[reg][3], sysregs[reg][4], sysregs[reg][5])
              print("{r}\t{v}".format(r = reg,v = out))
