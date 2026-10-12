# Cyber Sled (Namco 1993, System 21) decompile notes

Research/modding only, non-commercial. ROM set from the user's download `Downloads/Cyber-Sled_Arcade_EN.zip`
(inner MAME set `cybsled.zip`, 28 files), unpacked into `rom/`. No leaked source is used.

## Layout
- `rom/` the original ROM chips (never publish). `bin/` derived images (never publish).
- `interleave.py <upper> <lower> <out>`: 68000 16-bit bus, `-u` chip = even/high byte.
- `bin/mpr.bin` (cy2-mpr-u/l, 1 MB), `bin/spr.bin` (cy2-spr-u/l, 1 MB), `bin/data.bin` (cy1-data-u/l), `bin/edata0.bin` (cy1-edata0-u/l).
- `bin/<cpu>_flat.bin` = 4 MB image: program at 0, data at 0x200000, edata0 at 0x300000 (0x100000-0x1fffff zero = RAM/IO).
  The data mapping is provisional (to verify from code references).
- Ghidra project `ghidra/CyberSled.gpr`, programs `mpr_flat.bin` and `spr_flat.bin`, 68000:BE:32:default, base 0.
  Runner (chat scratchpad): `csrun.sh <abs log> <headless args>`; use forward-slash paths in args.
  Scripts: `ghidra/scripts/CsSetup.java` (64 vectors -> functions; run as -preScript on import), plus the Amok/Scorcher
  scripts via `-scriptPath C:/Users/john/Documents/Amok/ghidra/scripts` (ExportFuncInfo, DumpDecomp, ApplyNames, ...).

## First look (10-12)
- Both CPUs: SP 0x110000, reset PC 0x1000; same vector layout (handlers 0x100..0x398; irq7 0x100, traps 0-15 share 0x22a).
  The two programs share a library but differ in 909462 bytes.
- mpr: ROM used up to 0xfc0e2 (big tables), credit string "PROGRAMED by N.Aoshima & K.Watanabe".
- spr: used up to 0x7ff5d; holds the test mode / debug menus (POLYGON OBJECT TEST, SOUND TEST, COLOR CHECK, AD JUSTER, ...).
- After import + auto-analysis: mpr 513 functions, spr 468 (low: function discovery pass needed).
- Other chips: poi-* = point/model data for the DSP, obj* = sprites, snd0 = 6809 sound program, voi* = C140 samples, cybsled.nv = 8 KB EEPROM.

## Next
1. Function discovery (JSR/BSR targets, LINK/MOVEM prologues) on both CPUs.
2. Verify the memory map from code (RAM, shared RAM, DSP, sprite/C355, I/O) and add proper memory blocks.
3. Name passes, strings and test mode first (spr), then the game loop.

## Function discovery (10-12)
- `ghidra/scripts/CsCoverage.java <lo> <hi> [create]`: coverage + creates functions at code-looking undefined gaps
  (first nibble not 0/a/f). 3 iterations: mpr 513 -> 818 functions (0x100-0x40000: 136k instr, 114k undefined left),
  spr 468 -> 700 (0x100-0x20000). Abs JSR/JMP targets: mpr max 0x37a92, spr max 0x1f45e (code ends there; rest data).
- Memory map: cybsled is driven by MAME `src/mame/namco/namcos21_c67.cpp` (not namcos21.cpp = Winning Run). In the
  Winning Run map the data ROM is at 0x800000 (common map), so the flat image's 0x200000 data placement is probably WRONG:
  check namcos21_c67.cpp and rebuild the images / memory blocks.
- FIXED (10-12): real map from MAME namcos21_c67.cpp put into `ghidra/scripts/CsMap.java <master|slave>` (work RAM
  0x100000 (master 64K, slave 256K), nvram 0x180000 (master), C148 0x1c0000, DSP RAM 0x200000, pointram 0x400000/0x440000,
  C355 sprites 0x700000, palette 0x740000/0x750000, video enable 0x760000, data ROM 0x800000, shared RAM 0x900000,
  DPRAM 0xa00000, C139 0xb00000/0xb80000, edata ROM 0xc00000). Programs now `mpr.bin` / `spr.bin` (import bin/mpr.bin,
  bin/spr.bin at 0 with -preScript CsMap.java <cpu> -preScript CsSetup.java). The old *_flat.bin programs are obsolete.
- After 4 CsCoverage create rounds: mpr.bin 822 functions, spr.bin 676. funcinfo_mpr.bin.tsv / funcinfo_spr.bin.tsv.

## Name pass 1 (10-12)
- Six Sonnet agents read the CsDumpAll dumps; names in `ghidra/hand_spr.txt` (490) and `ghidra/hand_mpr.txt` (649),
  applied with Amok ApplyNames.java hand mode. Left FUN_: spr 175, mpr 159 (mostly small / bad-data stubs) -> round 2.
- Slave (spr): reset 0x1000 -> init chain 0x3acc / 0x3b10-0x4130, per-frame loop dispatches on 0x901c00 / 0x902012 /
  0x901d20 / 0x900210. IRQ 1/2/3/6 = 0x1682 vblank (frame counters 0x100004/6), IRQ5 0x1cfa link, IRQ4 0x37d8 C139 rx.
  Sprite list: 8-word entries via ptr 0x109000, order list 0x109004, count 0x109008 -> C355 0x710000/0x714000.
  Text = sprites (string struct ptr 0x105000, attr 0x105004; printers 0x106ac / 0x106c0). HUD 0x10000-0x1a800,
  math 0x1a806-0x1c8e4 (3x3 matrix 0x1ad16, projection 0x1c18a), test mode 0x1cb02-0x1f268, LFSR rng 0x107100,
  depth-cue palette ramps 0xda12-0xe048, C139 link 0x3188-0x3a20.
- Master (mpr): boot waits MCU handshake 0xa00074 == 0xa6; state table 0x1ba8 indexed by 0x100900; display list ptr
  0x100824 into DSP RAM 0x208200/0x20c200 (0xffff end). NVRAM sig/checksum 0x180000-0x18002d, counters 0x181000+.
  Inputs 0xa00000 (edge 0x100a12, held 0x100a10), sticks 0xa00010-16 minus centres 0x9002c0-c6; sound 0xa00420/0xa0043c.
  Tank array shared 0x904000 stride 0x100 (+0x14 flags, +0x50 team, own index 0x90020e), player pos 0x100100,
  health 0x901d02, shots 0x105800 (8 x 0x20), missiles 0x103a00, explosions 0x103800, pickups 0x906000,
  replay ring 0x906e00, rng x*5+1 at 0x100880, atan2 table 0x33616, enemy AI 0x1b2aa-0x23f94, level init 0x3dc12.
  (Agent-derived; verify before relying on any single address.)

## Round 2 + gap discovery (10-12)
- Round 2 agents named the leftovers: hand_spr.txt 638 lines, hand_mpr.txt 730; false functions (data tables / mid-
  instruction / halt_baddata) listed in ghidra/bogus_spr.txt (27) and bogus_mpr.txt (78), removed with Amok
  DeleteFunctions.java. After that: spr 649 functions, mpr 744, 0 FUN_.
- CsCoverage.java new mode `pseudo`: creates a function at any gap start that PseudoDisassembler.isValidSubroutine
  (must terminate) accepts, no first-nibble filter (0x0839 BTST / 0x0c79 CMPI gaps are real code). Fixpoint:
  spr 732 functions (undefined 37.5 KB left in 0x400-0x20000), mpr 864 (75 KB left in 0x400-0x38000; the last
  rounds only made 2 tiny stubs each = data chains, stopped). Round 3 naming on the 83 / 120 new FUN_.
- Round 3 (10-12) applied: spr 695 functions (684 hand + vectors), mpr 857 (843 hand), 0 FUN_ on both.
  bogus_spr.txt now 64, bogus_mpr.txt 85. OPEN: ~21 spr round-3 "bogus" entries are junk-prefix gaps (table bytes
  before real code: sprite emitters, gauge boxes, palette fade); their real entries are a few bytes later and are now
  orphan instructions. scratchpad ptrscan.py (be32 pointers to entry+k) found pointers for some (e.g. 0x3df4+0xe,
  0x7636+0x26, 0xb318+0xc, 0xb3e0+0xc, 0xec28+0xc). Next: orphan-entry pass (instructions in no function).

## Pointer-target pass + round 4 (10-12)
- ghidra/scripts/CsPtrFuncs.java <codeEnd> [create]: scans 0x400..0x100000 (even, outside instructions) for be32
  pointers into [0x400, codeEnd) that land on an orphan instruction or an undefined spot that isValidSubroutine
  accepts; prints "target <addr> orphan|undef sites ...". Dry run: spr 293 targets (224 orphan, 69 undef), mpr 534
  (389 orphan, 145 undef). ghidra/scripts/pfsel.py keeps a target with >= 2 sites or a site within +-4 of another
  site (tables), output = ptr_<a> hand lines: ghidra/ptr_spr.txt (266), ghidra/ptr_mpr.txt (472).
- ApplyNames hand on those created 258 functions in spr (953 total) and 397 in mpr (1254 total). Example: spr state
  jump table at 0x1c24..0x1c40 -> 0x1c9a, 0x1d30, 0x1f06, 0x225a, 0x25e6, 0x29ec, 0x2a68, 0x2c64, 0x2dc4.
- Round 4: three Sonnet agents name the ptr_ functions (spr, mpr halves); undef ones may be data -> bogus.
- Round 4 applied (10-12): spr 952 functions (941 hand), mpr 1237 (1223 hand), 0 FUN_/ptr_. Bogus: spr 0x1dfaa (mid-block
  entry into unrolled code); mpr 17 (round constants 0x8000/0xa800/0x3a00/0x3c3c/0x3d00/0x3e00/0x3e9a/0x4a72 were values,
  not pointers; 8 junk-prefix entries 0x13800.. ; 0x236fc). 0x482 (spr) kept: spr_cmd_wait_dispatch (jump table Ghidra
  truncates). Pointer rescan after round 4: spr 26, mpr 57 single-site leftovers = fixpoint.
- ghidra/scripts/CsOrphans.java <lo> <hi> [create|fixup]: runs of instructions owned by no function, with ref kinds
  (call/jump/data). Most orphans were bsr/jsr targets (Ghidra made no function); "create" makes a function only at
  called runs. 3 rounds: spr +128 (92/24/12), mpr +59 (41/15/3). Left after: spr 67 runs (5 call, 1 jump, 13 data, 48
  no refs), mpr 83 (0 call, 2 jump, 24 data, 57 no refs). fixup (fixupFunctionBody) grew only 7 bodies on mpr.
  Scratchpad d68.py <bin> <hexaddr> <n> = capstone 68000 disassembler.
- Next: round 5 naming of the new FUN_ (orphan-call functions), then the no-ref / data-ref orphan runs (junk-prefix
  entries; data refs = pointer from a table with one site).
- Rounds 5-6 applied (10-12): round 5 named the orphan-call functions (spr 128, mpr 59, all real); CsOrphans createref
  added spr 18 / mpr 25 data-ref functions, round 6: spr 12 func + 6 bogus, mpr 14 func + 11 bogus (garbage-prefix
  entries; mpr 0x11c08 = table base). Result: spr 1092 functions, mpr 1310, 0 FUN_/ptr_. Function discovery DONE;
  leftover orphan runs with no refs are data decoded as code. Skill cybersled-re created; csrun.sh, d68.py and the
  naming prompt r2_prompt.txt copied to ghidra/scripts.

## Globals pass (10-12, labels applied, provisional)
- ghidra/scripts/globs.py <decomp.c> <out>: DAT_ refs in work RAM 0x100000-0x1bffff and shared RAM 0x900000-0x90ffff
  with counts and user functions. spr 828 addresses (262 shared, 566 work), mpr 1536 (415 shared, 1121 work).
- Four Sonnet agents (prompt ghidra/scripts/gl_prompt.txt) write "0x<addr> <name>" lines (g_ work RAM, nv_ NVRAM, sh_
  shared): scratchpad gn_shared.txt (applies to both CPUs), gn_spr.txt, gn_mpr_a.txt, gn_mpr_b.txt. Apply with the Amok
  ApplyGlobals.java <file> (labels only, no types yet) into ghidra/globals_<cpu>.txt.
- Applied (10-12): ghidra/globals_spr.txt (486 shared + 566 work = 1052 labels) and ghidra/globals_mpr.txt (486 shared
  + 1121 work = 1607) with ApplyGlobals, 0 problems. PROVISIONAL: agents named from the user-function names only (no
  decompile reading), so many are generic (<base>_<hexoffset>, tank0_<field> at 0x904000 offsets). Refine during the
  types pass. Next: types pass (CommitParams / struct for the tank record 0x904000 stride 0x100), then repo.

## Types pass (10-12)
- Backup before: ghidra/CyberSled.rep.bak_types.
- Amok CommitParams.java apply: spr committed 1092 (params 14, non-void return 24); mpr committed 1309, failed 1
  (params 14, non-void return 167). Few params because 68000 code here passes values in registers/globals.
- Amok ExportSigs.java: ghidra/types_spr.txt (1658 lines), ghidra/types_mpr.txt (2383 lines).
- Re-exported funcinfo + decomp: spr 1092 functions, 0 decompile failures; mpr 1310, 1 failure
  (game_unk_0002f370, 22 bytes, decompiler process dies; already flagged in hand_mpr.txt).
- Tank struct at 0x904000 (stride 0x100) NOT defined: the field names are provisional; do it when refining globals.
- PUBLISHED 10-12: github.com/indieindie7/cybersled-decomp (commit fd30909; local clone Documents/github/cybersled-decomp).
  Next (optional): refine the provisional globals from the decompile, then define the tank struct.

## Paused (10-12): globals refinement + seat struct
- Findings so far: the "tank" block is a per-seat state record the master publishes for the slave
  (shared_publish_player_state 0x173a). Offset = cabinet id << 8 (0x90020e, set by game_init_player_vars and
  shared_select_cabinet_block from the table at 0x18e8), so blocks at 0x904000 and 0x904100, stride 0x100.
  0x905000 / 0x905100 (offsets 0x1000 / 0x1100 in 0x900a10) are used the same way. Several labels are misnamed:
  0x90020e is the own-seat offset (not an attract flag), 0x900204 the cabinet id, 0x900a10 a seat offset.
- Nothing applied yet. Resume: build the struct from the publish function, then the agent refinement.
- Reverify (10-12): ExportFuncInfo -readOnly -noanalysis: mpr 1310 / spr 1092 functions, 0 FUN_; CsDumpAll + globs.py:
  unlabelled RAM DAT_ left mpr 28, spr 19. Local hand/globals/types files equal to repo fd30909. Gotcha: headless
  WITHOUT -noanalysis re-analyses in memory and shows fake FUN_ / missing functions.
- Label fixes applied (both CPUs): 0x900204 sh_cabinet_id, 0x90020e sh_own_seat_offset, 0x900a10 sh_seat_offset_b.
  Seat struct still not defined (optional).
