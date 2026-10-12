# Cyber Sled (Namco, 1993) reverse-engineering notes and symbols

Hand-named function maps, global labels, Ghidra scripts and working notes for the arcade game
**Cyber Sled** (Namco System 21, "C67" board). The board runs two 68000 programs: the master `mpr`
(game logic) and the slave `spr` (HUD, sprites, palette, test mode). Same method as
[scorcher-decomp](https://github.com/indieindie7/scorcher-decomp) and
[amok-decomp](https://github.com/indieindie7/amok-decomp). Non-commercial, done for study and preservation.

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | the full working log: ROM layout, memory map, function discovery pipeline, every naming round, globals and types passes |
| `ghidra/hand_<cpu>.txt` | hand-named functions (`0x<addr> func <name> hand <comment>`); spr 1092 and mpr 1310 functions, no `FUN_` left |
| `ghidra/ptr_<cpu>.txt` | names for functions found through ROM pointer tables |
| `ghidra/bogus_<cpu>.txt` | false function starts that were deleted (data decoded as code, junk-prefix entries, round constants) |
| `ghidra/globals_<cpu>.txt` | labels for work RAM (`g_`), NVRAM (`nv_`) and shared RAM (`sh_`, `tank0_<field>` at 0x904000); **provisional** |
| `ghidra/types_<cpu>.txt` | committed function signatures |
| `ghidra/funcinfo_<cpu>.bin.tsv` | per-function export: address, name, size, callees, string references |
| `ghidra/scripts/` | headless Ghidra scripts (memory map, vectors, coverage, pointer-table and orphan-code discovery, decompile dump), a capstone 68000 disassembler, the naming prompts |
| `tools/interleave.py` | joins the upper/lower 16-bit ROM chips into one program image |

The shared scripts `ApplyNames.java`, `ExportFuncInfo.java`, `DeleteFunctions.java`, `ApplyGlobals.java`,
`CommitParams.java` and `ExportSigs.java` are in amok-decomp's `ghidra/scripts`.

## What is NOT here

No game files: no ROMs, no interleaved program images, no data dumps, no decompiled C output and no
Ghidra project database (which embeds the binaries). You need your own copy of the MAME set `cybsled`.

## Reproducing the Ghidra project

1. Interleave the program chips with `tools/interleave.py` (`-u` chip = even/high byte) into `mpr.bin` and `spr.bin`.
2. Ghidra 12.1.4: import each as 68000:BE:32:default at base 0, run `CsSetup.java` (vectors) and
   `CsMap.java master|slave` (memory map from MAME `namcos21_c67`).
3. Run amok-decomp's `ApplyNames.java` with `hand_<cpu>.txt` and `ptr_<cpu>.txt` in `hand` mode (it also
   creates the functions), `DeleteFunctions.java` with the `bogus_<cpu>.txt` addresses, then
   `ApplyGlobals.java globals_<cpu>.txt`.
