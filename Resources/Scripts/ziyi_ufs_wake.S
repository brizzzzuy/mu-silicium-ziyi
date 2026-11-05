// Hash-pinned ziyi UFSDxe, inside ufs_open's existing saved-register frame.
// X19 = handle; W20 = LUN. X21's core index was consumed at 0x9910 and is
// dead until the epilogue, so W21 records a successful early ACTIVE command.
// The native TUR and START STOP UNIT implementations and error paths remain.
.section .text.wake,"ax"
.balign 4
.global ZiyiUfsWake
ZiyiUfsWake:
    mov w21, wzr
    ldr x8, [x19]
    // Invalidate cached sense fields used below. A transport failure or a
    // truncated sense response must not recover using an earlier command's ASC.
    str wzr, [x8, #0x480]
    strh wzr, [x8, #0x48c]
    bl UfsTur
    cbz w0, UfsReadyResult
    cmn w0, #5
    b.ne UfsReadyResult
    ldr x8, [x19]
    ldrb w9, [x8, #0x480]
    and w9, w9, #0x7f
    cmp w9, #0x70
    b.ne UfsReadyResult
    ldrb w9, [x8, #0x482]
    and w9, w9, #0xf
    cmp w9, #2
    b.ne UfsReadyResult
    ldrb w9, [x8, #0x487]
    cmp w9, #6
    b.lo UfsReadyResult
    ldrb w9, [x8, #0x48c]
    cmp w9, #4
    b.ne UfsReadyResult
    ldrb w9, [x8, #0x48d]
    cmp w9, #2
    b.ne UfsReadyResult

    mov x0, x19
    mov w1, #1
    bl UfsActive
    cbnz w0, UfsReadyResult
    mov w21, #1
    mov x0, x19
    bl UfsTur
    b UfsReadyResult

.section .text.late,"ax"
.balign 4
.global ZiyiUfsLate
ZiyiUfsLate:
    cmp w20, #0xd0
    b.ne UfsAfterActive
    cbnz w21, UfsAfterActive
    b UfsOriginalActive
