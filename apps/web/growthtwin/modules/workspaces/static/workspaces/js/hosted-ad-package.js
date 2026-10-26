"use strict";
// A bounded ZIP_STORED writer, not an archive importer or arbitrary file API.
window.YaparoAdPackage = (() => {
  const draftNames = ["ad.png", "source.png", "draft.json", "manifest.json", "README.txt"];
  const encoder = new TextEncoder();
  const table = Array.from({length:256},(_,n) => {
    for (let i=0;i<8;i++) n = (n&1) ? (0xedb88320^(n>>>1)) : n>>>1;
    return n>>>0;
  });
  function crc(bytes) {
    let value = 0xffffffff;
    for (const byte of bytes) value = table[(value^byte)&255]^(value>>>8);
    return (value^0xffffffff)>>>0;
  }
  function zip(files, kind="draft") {
    if (!["draft","campaign"].includes(kind)) throw Error("kind");
    const names = kind==="campaign" ? [...draftNames,"campaign.json"] : draftNames;
    if (Object.keys(files).length !== names.length || names.some(n => !(files[n] instanceof Uint8Array))) throw Error("files");
    const chunks=[], central=[]; let offset=0, total=0;
    for (const name of names) {
      const data=files[name], encoded=encoder.encode(name);
      total+=data.length;
      if (data.length>8388608 || total>20971520) throw Error("size");
      const checksum=crc(data);
      const local=new Uint8Array(30+encoded.length), l=new DataView(local.buffer);
      l.setUint32(0,0x04034b50,true); l.setUint16(4,20,true); l.setUint16(12,33,true);
      l.setUint32(14,checksum,true); l.setUint32(18,data.length,true); l.setUint32(22,data.length,true); l.setUint16(26,encoded.length,true); local.set(encoded,30);
      const entry=new Uint8Array(46+encoded.length), c=new DataView(entry.buffer);
      c.setUint32(0,0x02014b50,true); c.setUint16(4,20,true); c.setUint16(6,20,true); c.setUint16(14,33,true);
      c.setUint32(16,checksum,true); c.setUint32(20,data.length,true); c.setUint32(24,data.length,true); c.setUint16(28,encoded.length,true); c.setUint32(42,offset,true); entry.set(encoded,46);
      chunks.push(local,data); central.push(entry); offset+=local.length+data.length;
    }
    const size=central.reduce((sum,part)=>sum+part.length,0), end=new Uint8Array(22), e=new DataView(end.buffer);
    e.setUint32(0,0x06054b50,true); e.setUint16(8,names.length,true); e.setUint16(10,names.length,true); e.setUint32(12,size,true); e.setUint32(16,offset,true);
    return new Blob([...chunks,...central,end],{type:"application/zip"});
  }
  return Object.freeze({zip});
})();
