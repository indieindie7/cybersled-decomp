// CsMap.java <master|slave>: System 21 (C67) memory map from MAME namcos21_c67.cpp (cybsled), added to a program
// imported from bin/mpr.bin or bin/spr.bin at base 0. Data ROMs come from bin/data.bin (0x800000) and
// bin/edata0.bin (0xc00000); everything else is an uninitialized volatile block (RAM / I/O).
//@category CyberSled
import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.*;
import java.io.*;
public class CsMap extends GhidraScript {
  Memory m;
  void io(String n, long a, long len, boolean vol) throws Exception {
    MemoryBlock b = m.createUninitializedBlock(n, toAddr(a), len, false);
    b.setRead(true); b.setWrite(true); b.setVolatile(vol);
  }
  void rom(String n, long a, String file) throws Exception {
    File f = new File("C:/Users/john/Documents/CyberSled/bin/" + file);
    try (InputStream in = new FileInputStream(f)) {
      MemoryBlock b = m.createInitializedBlock(n, toAddr(a), in, f.length(), monitor, false);
      b.setRead(true); b.setWrite(false);
    }
  }
  public void run() throws Exception {
    boolean master = getScriptArgs()[0].equals("master");
    m = currentProgram.getMemory();
    io("work_ram", 0x100000, master ? 0x10000 : 0x40000, false);
    if (master) io("nvram", 0x180000, 0x4000, true);
    io("c148_intc", 0x1c0000, 0x40000, true);
    io("dsp_ram", 0x200000, 0x10000, true);
    io("io_280000", 0x280000, 2, true);
    io("pointram_ctl", 0x400000, 2, true);
    io("pointram_data", 0x440000, 0x40000, true);
    io("depthcue", 0x480000, 0x800, true);
    io("c355_spriteram", 0x700000, 0x20000, true);
    io("c355_position", 0x720000, 8, true);
    io("palette", 0x740000, 0x10000, true);
    io("palette_ext", 0x750000, 0x10000, true);
    io("video_enable", 0x760000, 2, true);
    rom("data_rom", 0x800000, "data.bin");
    io("shared_ram", 0x900000, 0x10000, false);
    io("dpram", 0xa00000, 0x1000, true);
    io("c139_ram", 0xb00000, 0x4000, true);
    io("c139_regs", 0xb80000, 0x10, true);
    rom("edata_rom", 0xc00000, "edata0.bin");
    println("map: " + m.getBlocks().length + " blocks");
  }
}
