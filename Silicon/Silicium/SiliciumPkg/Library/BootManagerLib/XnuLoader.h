#ifndef _XNU_LOADER_H_
#define _XNU_LOADER_H_

//
// The boot shim (built with PAYLOAD_BASE, as HakiOS's mkxnuimg.py does) copies everything appended
// after the UEFI FD to this address, which the device memory map keeps reserved. A device opts in by
// giving the address from its .dsc (ziyi: -D XNU_PAYLOAD_BASE=0xB0000000ULL, the same number as
// HakiOS's devices/<name>/boot.conf); on every other device the boot manager never calls the loader.
//
#ifdef XNU_PAYLOAD_BASE
#define XNU_LOADER_ENABLED    1
#else
#define XNU_LOADER_ENABLED    0
#define XNU_PAYLOAD_BASE      0xF0000000ULL
#endif
#define XNU_PAYLOAD_MAX_SIZE  0x04000000ULL
#define XNU_PAYLOAD_MAGIC     0x50554E58 // "XNUP"

typedef struct {
  UINT32 Magic;
  UINT32 Size;
} XNU_PAYLOAD_HEADER;

// The header is followed by entries; an empty name ends the list.
typedef struct {
  CHAR8  Name[16];
  UINT32 Size;
  UINT32 Reserved;
  // UINT8 Data[Size], padded to 16 bytes
} XNU_PAYLOAD_ENTRY;

// Raw GPT partition that receives the text log (read back from Android).
#define XNU_LOG_PARTITION  L"logdump"

#define XNU_MARKER_MAGIC  0x584E5521 // "XNU!"

VOID
XnuLoaderMain ();

#endif /* _XNU_LOADER_H_ */
