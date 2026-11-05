// Post-ABL write ownership check for the hash-pinned ziyi SPMIDxe.
// Inserted at RVA 0x3684, after argument validation and bytes-transferred = 0.
// X23 = bus context; W1 = opcode (0 write, 1 read); W3 = EE; W4 = local APID.
// Six-byte channel cache entries are populated from the hardware owner table;
// byte 1 bits [4:0] hold the write owner. Observer reads need not own the APID.
.section .text
.balign 4
.global ziyi_spmi_write_guard
ziyi_spmi_write_guard:
    cbnz w1, .Lcontinue
    ldr x9, [x23, #0x20]
    mov w10, #6
    umaddl x9, w4, w10, x9
    ldrb w9, [x9, #1]
    and w9, w9, #0x1f

    cmp w9, w3
    b.ne SpmiDenied


.Lcontinue:
    // Restore flags from the original CMP at 0x367c before B.EQ at 0x3688.
    cmp w1, #1
    ldrh w9, [x23, #0x44]
    b SpmiResume

