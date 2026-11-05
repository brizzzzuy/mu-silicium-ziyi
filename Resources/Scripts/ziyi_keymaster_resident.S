// Bootstrap cannot call public StartApp: that entry invokes bootstrap itself.
// Use the same native read-only lookup as public StartApp, before image loading.
.section .text.resident,"ax",%progbits
.global ZiyiKeymasterResident
ZiyiKeymasterResident:
    stp x29, x30, [sp, #-0x10]!
    adr x0, Keymaster64Name
    bl QseeLookupApp
    add w8, w0, #1
    cmp w8, #1
    b.hi ResidentFound
    adr x0, KeymasterName
    bl QseeLookupApp
    add w8, w0, #1
    cmp w8, #1
    b.hi ResidentFound
    ldp x29, x30, [sp], #0x10
    // Displaced ADRP at 0x3060; resume the untouched GUID loading path.
    adrp x1, QseeData
    b QseeGuidSetup
ResidentFound:
    stur w0, [x29, #-4]
    ldp x29, x30, [sp], #0x10
    mov x0, xzr
    b QseeBootstrapReturn
KeymasterName:
    .asciz "keymaster"
Keymaster64Name:
    .asciz "keymaster64"
