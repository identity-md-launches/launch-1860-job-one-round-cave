// Offline conversion of the delivered, noninterlaced 8-bit RGB(A) PNGs.
// Node built-ins + vendored jpeg-js. No network, environment or configuration reads.
// Usage: node gathering/thumbnail.js WORKSPACE.png SIZE QUALITY > preview.jpg
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const encode = require('./vendor/jpeg-js/encoder.js');

function crc32(bytes) {
  let crc = 0xffffffff;
  for (const value of bytes) {
    crc ^= value;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function decode(bytes) {
  if (!bytes.subarray(0, 8).equals(Buffer.from('89504e470d0a1a0a', 'hex')))
    throw new Error('not a PNG');
  let width, height, channels, ended = false;
  const idat = [];
  for (let offset = 8; offset < bytes.length;) {
    if (offset + 12 > bytes.length) throw new Error('truncated PNG');
    const size = bytes.readUInt32BE(offset);
    const end = offset + 8 + size;
    if (end + 4 > bytes.length) throw new Error('truncated chunk');
    const type = bytes.toString('ascii', offset + 4, offset + 8);
    if (crc32(bytes.subarray(offset + 4, end)) !== bytes.readUInt32BE(end))
      throw new Error('PNG CRC mismatch');
    const data = bytes.subarray(offset + 8, end);
    if (type === 'IHDR') {
      if (width !== undefined || size !== 13) throw new Error('invalid IHDR');
      width = data.readUInt32BE(0); height = data.readUInt32BE(4);
      if (!width || !height || width * height > 16777216 || data[8] !== 8 ||
          ![2, 6].includes(data[9]) || data[10] || data[11] || data[12])
        throw new Error('requires noninterlaced 8-bit RGB(A), at most 16M pixels');
      channels = data[9] === 2 ? 3 : 4;
    } else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') { ended = true; break; }
    offset = end + 4;
  }
  if (!ended || !width || !idat.length) throw new Error('incomplete PNG');
  const stride = width * channels;
  const raw = zlib.inflateSync(Buffer.concat(idat), {maxOutputLength: height * (stride + 1)});
  if (raw.length !== height * (stride + 1)) throw new Error('wrong scanline size');
  const pixels = Buffer.alloc(height * stride);
  for (let y = 0; y < height; y++) {
    const filter = raw[y * (stride + 1)];
    if (filter > 4) throw new Error('unknown PNG filter');
    for (let x = 0; x < stride; x++) {
      const index = y * stride + x;
      const a = x >= channels ? pixels[index - channels] : 0;
      const b = y ? pixels[index - stride] : 0;
      const c = y && x >= channels ? pixels[index - stride - channels] : 0;
      let prediction = 0;
      if (filter === 1) prediction = a;
      if (filter === 2) prediction = b;
      if (filter === 3) prediction = (a + b) >>> 1;
      if (filter === 4) {
        const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
        prediction = pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
      }
      pixels[index] = (raw[y * (stride + 1) + x + 1] + prediction) & 255;
    }
  }
  return {width, height, channels, pixels};
}

function thumbnail(input, size, quality) {
  const {width, height, channels, pixels} = decode(input);
  if (width !== height) throw new Error('wall must be square');
  if (!Number.isInteger(size) || size < 8 || size > width || size > 1024 ||
      !Number.isInteger(quality) || quality < 1 || quality > 100) throw new Error('invalid size/quality');
  const data = Buffer.alloc(size * size * 4, 255);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const x0 = Math.floor(x * width / size), x1 = Math.floor((x + 1) * width / size);
    const y0 = Math.floor(y * height / size), y1 = Math.floor((y + 1) * height / size);
    const sum = [0, 0, 0], count = (x1 - x0) * (y1 - y0);
    for (let sy = y0; sy < y1; sy++) for (let sx = x0; sx < x1; sx++) {
      const p = (sy * width + sx) * channels;
      if (channels === 4 && pixels[p + 3] !== 255) throw new Error('wall must be opaque');
      for (let c = 0; c < 3; c++) sum[c] += pixels[p + c];
    }
    for (let c = 0; c < 3; c++) data[(y * size + x) * 4 + c] = Math.round(sum[c] / count);
  }
  return encode({width: size, height: size, data}, quality).data;
}

if (require.main === module) {
  try {
    const input = fs.realpathSync(process.argv[2]);
    const relative = path.relative(fs.realpathSync('.'), input);
    if (relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative))
      throw new Error('input must stay inside workspace');
    if (fs.statSync(input).size > 32 * 1024 * 1024) throw new Error('PNG exceeds 32 MiB');
    process.stdout.write(thumbnail(fs.readFileSync(input), Number(process.argv[3]), Number(process.argv[4])));
  } catch (error) { console.error(error.message); process.exitCode = 2; }
}
module.exports = {decode, thumbnail};
