// CsSetup.java: 68000 vector table -> functions. Marks 0x0..0xff as 64 pointers, creates a function
// at every vector target inside program ROM (0..0xfffff), names reset/exception/interrupt handlers.
//@category CyberSled
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.symbol.SourceType;
import java.util.*;
public class CsSetup extends GhidraScript {
  static final String[] NAMES = {"vec_InitSP", "Reset", "BusError", "AddressError", "IllegalInstr", "ZeroDivide",
    "ChkInstr", "TrapV", "Privilege", "Trace", "Line1010", "Line1111"};
  public void run() throws Exception {
    Map<Long, String> made = new LinkedHashMap<>();
    for (int i = 0; i < 64; i++) {
      Address a = toAddr(4L * i);
      clearListing(a, a.add(3));
      createData(a, PointerDataType.dataType);
      if (i == 0) continue;
      long t = getInt(a) & 0xffffffffL;
      if (t == 0 || t >= 0x100000 || (t & 1) != 0) continue;
      String n;
      if (i < NAMES.length) n = "exc_" + NAMES[i];
      else if (i >= 24 && i <= 31) n = (i == 24 ? "exc_Spurious" : "irq_Level" + (i - 24));
      else if (i >= 32 && i <= 47) n = "trap_" + (i - 32);
      else n = "vec_" + i;
      if (made.containsKey(t)) { made.put(t, made.get(t) + "_" + n); continue; }
      made.put(t, n);
    }
    for (Map.Entry<Long, String> e : made.entrySet()) {
      Address t = toAddr(e.getKey());
      disassemble(t);
      createFunction(t, null);
      String n = e.getValue().length() > 60 ? e.getValue().substring(0, 60) : e.getValue();
      createLabel(t, n, true, SourceType.USER_DEFINED);
      println(String.format("%06x %s", e.getKey(), e.getValue()));
    }
    println("vectors: " + made.size() + " targets");
  }
}
