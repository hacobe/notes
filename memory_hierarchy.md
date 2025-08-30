# The Memory Hierarchy

Modern computer systems use multiple storage technologies with different performance characteristics. SRAM provides the fastest access but costs the most per bit. DRAM offers moderate speed at lower cost. SSDs and rotating disks provide large capacity at low cost but slower access. Programs achieve good performance by exploiting locality—the tendency to access the same data repeatedly or to access nearby data. The memory hierarchy organizes these storage technologies into levels, with faster, smaller storage at the top holding recently accessed data from slower, larger storage below.

## Storage Technologies

RAM comes in two varieties. Static RAM is faster and more expensive than dynamic RAM. Cache memories use SRAM while main memory uses DRAM.

Disks have much larger capacity than RAM at much lower cost per bit, but are much slower. They rely on mechanical spinning parts to access data, while RAM accesses data electronically.

Solid state disks are flash memory-based storage devices that are faster than rotating disks, particularly for reads, but are more expensive per bit.

From 1985 to 2015, DRAM and disk costs dropped dramatically while their access speeds barely improved, creating a widening gap with processor speeds. SRAM kept pace with processor speeds but its high cost has limited it to small caches. SSDs became mainstream after 2008, filling part of the performance gap between DRAM and rotating disks.

## Locality

Locality has two forms. Temporal locality means a memory location referenced once is likely to be referenced again multiple times in the near future. Spatial locality means if a memory location is referenced once, the program is likely to reference a nearby memory location in the near future.

Programs exhibit locality through their data access patterns. C stores arrays in row-major order, with elements laid out row by row in memory. The `sumarrayrows` function below maintains good spatial locality by traversing elements in their storage order. Each memory access follows the previous one sequentially.

```C
// Good spatial locality
int sumarrayrows(int a[M][N]) {
   for (i = 0; i < M; i++)
       for (j = 0; j < N; j++)
           sum += a[i][j];
}
```

The `sumarraycols` function accesses elements column-wise, jumping through memory rather than accessing consecutive locations, resulting in poor spatial locality.

```C
// Poor spatial locality
int sumarraycols(int a[M][N]) {
   for (j = 0; j < N; j++)
       for (i = 0; i < M; i++)
           sum += a[i][j];
}
```

Program instructions stored in memory must be fetched by the CPU. Loop instructions execute in sequential memory order, providing good spatial locality. Since loop bodies execute multiple times, they also exhibit good temporal locality. Smaller loop bodies with more iterations yield better locality.

## The Memory Hierarchy

The memory hierarchy consists of seven storage levels. At the top are CPU registers, followed by three SRAM caches, DRAM main memory, local disks, and remote secondary storage at the bottom. Remote secondary storage includes distributed file systems and Web servers.

CPU registers hold words retrieved from the first cache. The first cache holds cache lines retrieved from the second cache. The second cache holds cache lines retrieved from the third cache. The third cache holds cache lines retrieved from main memory. Main memory holds disk blocks retrieved from local disks. Local disks hold files retrieved from remote network servers.

Storage devices are smaller, faster, and more expensive per byte at higher levels. They are larger, slower, and cheaper per byte at lower levels.

## Sources

* "6 The Memory Hierarchy", Computer Systems: A Programmer's Perspective