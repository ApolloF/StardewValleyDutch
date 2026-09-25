"""Minimal XNB reader for Stardew Valley content (LZX / LZ4 / uncompressed).

Supports: raw decompression, Dictionary<string,string>, Texture2D (Color) -> PNG.
LZX decoder ported from MonoGame's LzxDecoder (itself from libmspack).
"""
import struct, sys, zlib, json, os

# ---------------------------------------------------------------- LZX
MIN_MATCH, NUM_CHARS = 2, 256
BT_VERBATIM, BT_ALIGNED, BT_UNCOMPRESSED = 1, 2, 3
NUM_PRIMARY_LENGTHS, NUM_SECONDARY_LENGTHS = 7, 249

EXTRA_BITS = [0] * 52
_j = 0
for _i in range(0, 51, 2):
    EXTRA_BITS[_i] = _j
    EXTRA_BITS[_i + 1] = _j
    if _i != 0 and _j < 17:
        _j += 1
POSITION_BASE = [0] * 51
_j = 0
for _i in range(51):
    POSITION_BASE[_i] = _j
    _j += 1 << EXTRA_BITS[_i]


def build_table(lengths):
    """Canonical Huffman -> 16-bit lookup list of (sym, len)."""
    table = [None] * 65536
    code = 0
    for L in range(1, 17):
        for sym, l in enumerate(lengths):
            if l == L:
                span = 1 << (16 - L)
                start = code << (16 - L)
                if start + span > 65536:
                    raise ValueError("bad huffman table")
                entry = (sym, L)
                for k in range(start, start + span):
                    table[k] = entry
                code += 1
        code <<= 1
    return table


class Lzx:
    def __init__(self, window_bits=16):
        self.wsize = 1 << window_bits
        self.window = bytearray(self.wsize)
        posn_slots = {15: 30, 16: 32, 17: 34, 18: 36, 19: 38, 20: 42, 21: 50}[window_bits]
        self.main_elements = NUM_CHARS + (posn_slots << 3)
        self.R0 = self.R1 = self.R2 = 1
        self.header_read = False
        self.block_remaining = 0
        self.block_length = 0
        self.block_type = 0
        self.wpos = 0
        self.main_len = [0] * (NUM_CHARS + 50 * 8)
        self.length_len = [0] * (NUM_SECONDARY_LENGTHS + 1)
        self.intel_started = False
        self.intel_filesize = 0

    # bit buffer --------------------------------------------------------
    def _init_bits(self, data, pos):
        self.data = data
        self.pos = pos
        self.bitbuf = 0
        self.bitsleft = 0

    def _ensure(self, n):
        while self.bitsleft < n:
            d = self.data
            p = self.pos
            lo = d[p] if p < len(d) else 0
            hi = d[p + 1] if p + 1 < len(d) else 0
            self.pos = p + 2
            self.bitbuf |= ((hi << 8) | lo) << (16 - self.bitsleft)
            self.bitsleft += 16

    def _read(self, n):
        if n == 0:
            return 0
        self._ensure(n)
        v = self.bitbuf >> (32 - n)
        self.bitbuf = (self.bitbuf << n) & 0xFFFFFFFF
        self.bitsleft -= n
        return v

    def _sym(self, table):
        self._ensure(16)
        e = table[self.bitbuf >> 16]
        if e is None:
            raise ValueError("bad huffman code")
        sym, L = e
        self.bitbuf = (self.bitbuf << L) & 0xFFFFFFFF
        self.bitsleft -= L
        return sym

    def _read_lengths(self, lens, first, last):
        pre = [self._read(4) for _ in range(20)]
        pt = build_table(pre)
        x = first
        while x < last:
            z = self._sym(pt)
            if z == 17:
                y = self._read(4) + 4
                for _ in range(y):
                    lens[x] = 0; x += 1
            elif z == 18:
                y = self._read(5) + 20
                for _ in range(y):
                    lens[x] = 0; x += 1
            elif z == 19:
                y = self._read(1) + 4
                z = self._sym(pt)
                z = lens[x] - z
                if z < 0: z += 17
                for _ in range(y):
                    lens[x] = z; x += 1
            else:
                z = lens[x] - z
                if z < 0: z += 17
                lens[x] = z; x += 1

    def decompress(self, data, pos, in_len, out_len):
        self._init_bits(data, pos)
        endpos = pos + in_len
        if not self.header_read:
            if self._read(1):
                i = self._read(16); j = self._read(16)
                self.intel_filesize = (i << 16) | j
            self.header_read = True
        togo = out_len
        win = self.window
        wsize = self.wsize
        while togo > 0:
            if self.block_remaining == 0:
                if self.block_type == BT_UNCOMPRESSED:
                    if self.block_length & 1:
                        self.pos += 1
                    self.bitbuf = 0; self.bitsleft = 0
                self.block_type = self._read(3)
                i = self._read(16); j = self._read(8)
                self.block_remaining = self.block_length = (i << 8) | j
                bt = self.block_type
                if bt == BT_ALIGNED:
                    al = [self._read(3) for _ in range(8)]
                    self.aligned_table = build_table(al)
                if bt in (BT_ALIGNED, BT_VERBATIM):
                    self._read_lengths(self.main_len, 0, 256)
                    self._read_lengths(self.main_len, 256, self.main_elements)
                    self.main_table = build_table(self.main_len[:self.main_elements])
                    if self.main_len[0xE8] != 0:
                        self.intel_started = True
                    self._read_lengths(self.length_len, 0, NUM_SECONDARY_LENGTHS)
                    self.length_table = build_table(self.length_len[:NUM_SECONDARY_LENGTHS])
                elif bt == BT_UNCOMPRESSED:
                    self.intel_started = True
                    self._ensure(16)
                    if self.bitsleft > 16:
                        self.pos -= 2
                    self.bitbuf = 0; self.bitsleft = 0
                    self.R0, self.R1, self.R2 = struct.unpack_from("<III", self.data, self.pos)
                    self.pos += 12
                else:
                    raise ValueError("bad block type %d" % bt)

            while self.block_remaining > 0 and togo > 0:
                this_run = min(self.block_remaining, togo)
                togo -= this_run
                self.block_remaining -= this_run
                self.wpos &= wsize - 1
                if self.wpos + this_run > wsize:
                    raise ValueError("window overrun")
                bt = self.block_type
                if bt == BT_UNCOMPRESSED:
                    win[self.wpos:self.wpos + this_run] = self.data[self.pos:self.pos + this_run]
                    self.pos += this_run
                    self.wpos += this_run
                    continue
                aligned = bt == BT_ALIGNED
                while this_run > 0:
                    me = self._sym(self.main_table)
                    if me < NUM_CHARS:
                        win[self.wpos] = me
                        self.wpos += 1
                        this_run -= 1
                        continue
                    me -= NUM_CHARS
                    mlen = me & NUM_PRIMARY_LENGTHS
                    if mlen == NUM_PRIMARY_LENGTHS:
                        mlen += self._sym(self.length_table)
                    mlen += MIN_MATCH
                    moff = me >> 3
                    if moff > 2:
                        if not aligned:
                            if moff != 3:
                                extra = EXTRA_BITS[moff]
                                moff = POSITION_BASE[moff] - 2 + self._read(extra)
                            else:
                                moff = 1
                        else:
                            extra = EXTRA_BITS[moff]
                            moff = POSITION_BASE[moff] - 2
                            if extra > 3:
                                moff += self._read(extra - 3) << 3
                                moff += self._sym(self.aligned_table)
                            elif extra == 3:
                                moff += self._sym(self.aligned_table)
                            elif extra > 0:
                                moff += self._read(extra)
                            else:
                                moff = 1
                        self.R2, self.R1, self.R0 = self.R1, self.R0, moff
                    elif moff == 0:
                        moff = self.R0
                    elif moff == 1:
                        moff = self.R1
                        self.R1, self.R0 = self.R0, moff
                    else:
                        moff = self.R2
                        self.R2, self.R0 = self.R0, moff
                    this_run -= mlen
                    dest = self.wpos
                    if dest >= moff:
                        src = dest - moff
                    else:
                        src = dest + (wsize - moff)
                    for _ in range(mlen):
                        win[dest] = win[src]
                        dest += 1
                        src = (src + 1) & (wsize - 1)
                    self.wpos = dest
                if this_run < 0:
                    # match overran the frame; mirrors libmspack behaviour
                    raise ValueError("match overran frame")
        start = (self.wpos if self.wpos else wsize) - out_len
        out = bytes(win[start:start + out_len])
        if self.intel_started and self.intel_filesize:
            raise NotImplementedError("intel E8 translation")
        return out


def lzx_xnb(data, pos, end, out_size):
    dec = Lzx(16)
    out = bytearray()
    while pos < end:
        hi = data[pos]; lo = data[pos + 1]
        block_size = (hi << 8) | lo
        frame_size = 0x8000
        if hi == 0xFF:
            frame_size = (lo << 8) | data[pos + 2]
            block_size = (data[pos + 3] << 8) | data[pos + 4]
            pos += 5
        else:
            pos += 2
        if block_size == 0 or frame_size == 0:
            break
        out += dec.decompress(data, pos, block_size, frame_size)
        pos += block_size
        if len(out) >= out_size:
            break
    return bytes(out[:out_size])


def lz4_block(src, out_size):
    dst = bytearray()
    i = 0
    n = len(src)
    while i < n:
        tok = src[i]; i += 1
        lit = tok >> 4
        if lit == 15:
            while True:
                b = src[i]; i += 1; lit += b
                if b != 255: break
        dst += src[i:i + lit]; i += lit
        if i >= n: break
        off = src[i] | (src[i + 1] << 8); i += 2
        ml = tok & 15
        if ml == 15:
            while True:
                b = src[i]; i += 1; ml += b
                if b != 255: break
        ml += 4
        s = len(dst) - off
        for k in range(ml):
            dst.append(dst[s + k])
    return bytes(dst[:out_size])


def read_xnb_raw(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:3] == b"XNB", path
    flags = data[5]
    total = struct.unpack_from("<I", data, 6)[0]
    if flags & 0x80:
        dsize = struct.unpack_from("<I", data, 10)[0]
        return lzx_xnb(data, 14, total, dsize)
    if flags & 0x40:
        dsize = struct.unpack_from("<I", data, 10)[0]
        return lz4_block(data[14:total], dsize)
    return data[10:total]


# ---------------------------------------------------------------- content
class Reader:
    def __init__(self, b):
        self.b = b; self.p = 0

    def u8(self):
        v = self.b[self.p]; self.p += 1; return v

    def i32(self):
        v = struct.unpack_from("<i", self.b, self.p)[0]; self.p += 4; return v

    def u32(self):
        v = struct.unpack_from("<I", self.b, self.p)[0]; self.p += 4; return v

    def v7(self):
        r = 0; s = 0
        while True:
            b = self.u8(); r |= (b & 0x7F) << s; s += 7
            if not b & 0x80: return r

    def s(self):
        n = self.v7(); v = self.b[self.p:self.p + n].decode("utf-8"); self.p += n; return v

    def header(self):
        n = self.v7()
        self.readers = [(self.s(), self.i32()) for _ in range(n)]
        self.shared = self.v7()
        return self.readers


_DICT = "Microsoft.Xna.Framework.Content.DictionaryReader`2[["
_LIST_STR = "Microsoft.Xna.Framework.Content.ListReader`1[[System.String,"


def read_xnb(path):
    """Return (kind, value): 'dict' (str or int keys -> str), 'list' (str), 'texture', or 'raw'."""
    raw = read_xnb_raw(path)
    r = Reader(raw)
    readers = r.header()
    main = readers[0][0]
    if main.startswith(_DICT):
        key_t, val_t = [t.split(",", 1)[0] for t in main[len(_DICT):].split("],[", 1)]
        if key_t in ("System.String", "System.Int32") and val_t == "System.String":
            r.v7()
            n = r.i32()
            d = {}
            for _ in range(n):
                if key_t == "System.String":
                    r.v7(); k = r.s()
                else:
                    k = str(r.i32())
                t = r.v7()
                d[k] = r.s() if t else None
            return "dict", d
    if main.startswith(_LIST_STR):
        r.v7()
        items = []
        for _ in range(r.i32()):
            t = r.v7()
            items.append(r.s() if t else None)
        return "list", items
    if main.startswith("Microsoft.Xna.Framework.Content.Texture2DReader"):
        r.v7()
        fmt = r.i32(); w = r.u32(); h = r.u32(); levels = r.u32()
        size = r.u32()
        px = r.b[r.p:r.p + size]
        return "texture", (fmt, w, h, px)
    return "raw", (readers, raw)


def write_png(path, w, h, rgba):
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def unpremultiply(px):
    out = bytearray(px)
    for i in range(0, len(out), 4):
        a = out[i + 3]
        if 0 < a < 255:
            for c in range(3):
                out[i + c] = min(255, out[i + c] * 255 // a)
    return bytes(out)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    kind, val = read_xnb(src)
    if kind in ("dict", "list"):
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(val, f, ensure_ascii=False, indent=2)
    elif kind == "texture":
        fmt, w, h, px = val
        assert fmt == 0, fmt
        write_png(dst, w, h, unpremultiply(px))
    else:
        readers, raw = val
        with open(dst, "wb") as f:
            f.write(raw)
        print("raw:", [r[0][:120] for r in readers])
    print(kind, dst)


def read_spritefont_chars(path):
    """Set of characters a SpriteFont .xnb can draw."""
    r = Reader(read_xnb_raw(path))
    r.header()
    r.v7(); r.v7()
    r.i32(); r.u32(); r.u32(); r.u32()
    size = r.u32(); r.p += size
    for _ in range(2):
        r.v7(); n = r.i32(); r.p += 16 * n
    r.v7(); n = r.i32()
    chars = set()
    for _ in range(n):
        b0 = r.b[r.p]
        ln = 1 if b0 < 0x80 else 2 if b0 < 0xE0 else 3 if b0 < 0xF0 else 4
        chars.add(r.b[r.p:r.p + ln].decode("utf-8")); r.p += ln
    return chars
