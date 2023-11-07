#include <iostream>
#include <vector>
#include <cmath>
#include <thread>

int *getDim(float x, float y, float width, float length, float resolution)
{
  // compute how big one pixel is
  float pixSize = 1.0 / resolution;

  // round up the width and length to the nearest pixel
  float newWidth = ceil(width / pixSize) * pixSize;
  float newLength = ceil(length / pixSize) * pixSize;

  // set limits
  float xMin = x;
  float xMax = x + newWidth;

  float yMin = y;
  float yMax = y + newLength;

  // how many pixes wide and long is the region?
  int widthPix = ceil(width / pixSize);
  int lengthPix = ceil(length / pixSize);

  // make an int tuple
  int *pixCount = new int[2];
  pixCount[0] = widthPix;
  pixCount[1] = lengthPix;

  return pixCount;
}

void getRegionWorker(int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float z, float width, float length, float resolution, int scanStart, int scanEnd, int64_t *region, int *hits)
{

  // compute how big one pixel is
  float pixSize = 1.0 / resolution;
  float pixSizeRecip = resolution;

  // round up the width and length to the nearest pixel
  float newWidth = ceil(width / pixSize) * pixSize;
  float newLength = ceil(length / pixSize) * pixSize;

  // set limits
  float xMin = x;
  float xMax = x + newWidth;

  float yMin = y;
  float yMax = y + newLength;

  // how many pixes wide and long is the region?
  int widthPix = ceil(width / pixSize);
  int lengthPix = ceil(length / pixSize);

  // 0 the allocated region
  for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
  {
    region[ptr] = 0;
  }

  // 0 the hits
  for (int i = 0; i < widthPix * lengthPix; i++)
  {
    hits[i] = 0;
  }

  // for each scan
  for (int scan = scanStart; scan < scanEnd; scan++)
  {
    // get the start position of the scan
    int scanBeginIndex = scan * scanLength;

    // get the start position of the position data
    int posBeginIndex = scan * 4;

    // get x, y, z, angle of the scan
    float scanX = positions[posBeginIndex];
    float scanY = positions[posBeginIndex + 1];
    float scanZ = positions[posBeginIndex + 2];
    float angle = positions[posBeginIndex + 3];

    float zDiff = scanZ - z;
    float zDist = zDiff * zDiff;
    // iterate over the region
    int pixIndex = 0;

    float pixPosYdiff = scanY - yMin;
    for (int pixY = 0; pixY < lengthPix; pixY++)
    {

      // compute the x and z components of the distance between the scan and the pixel
      float yDist = pixPosYdiff * pixPosYdiff;
      pixPosYdiff -= pixSize;

      float pixPosXdiff = scanX - xMin;

      for (int pixX = 0; pixX < widthPix; pixX++)
      {

        // compute the distance
        float dist = sqrt(yDist + zDist + pixPosXdiff * pixPosXdiff);
        pixPosXdiff -= pixSize;

        // increment the pixel index
        pixIndex++;

        // are we within range of the radar?
        if (dist > binEnd || dist < binStart)
        {
          continue;
        }

        // get the bin number
        int bin = (dist - binStart) / binSize;

        // get the value of the bin
        int binValue = scans[scanBeginIndex + bin];

        // update the pixel value
        region[pixIndex] += binValue;
        hits[pixIndex]++;
      }
    }
  }
}

float *getRegion(int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float z, float width, float length, float resolution)
{
  // split the work into max-2 threads
  int nthreads = std::thread::hardware_concurrency();
  std::cout << "Detected " << nthreads << " threads.\nUsing " << nthreads - 2 << " threads for computation.\n";

  std::cout << "Scan count: " << scanCount << "\n";

  int threadCount = nthreads - 2;

  // get the dimension of the region
  int *dim = getDim(x, y, width, length, resolution);
  int widthPix = dim[0];
  int lengthPix = dim[1];

  // allocate blocks of memory for the region
  std::vector<int64_t *> regions;

  for (int i = 0; i < threadCount; i++)
  {
    int64_t *region = new int64_t[widthPix * lengthPix];
    regions.push_back(region);
  }

  // same for hits
  std::vector<int *> hits;

  for (int i = 0; i < threadCount; i++)
  {
    int *hit = new int[widthPix * lengthPix];
    hits.push_back(hit);
  }

  // split the work into threads
  int scanPerThread = scanCount / threadCount;
  std::vector<std::thread> threads;

  for (int i = 0; i < threadCount; i++)
  {
    int scanStart = i * scanPerThread;
    int scanEnd = (i + 1) * scanPerThread;

    if (i == threadCount - 1)
    {
      scanEnd = scanCount;
    }

    std::thread t(getRegionWorker, scans, positions, scanCount, scanLength, binStart, binEnd, binSize, x, y, z, width, length, resolution, scanStart, scanEnd, regions[i], hits[i]);

    threads.push_back(std::move(t));
  }

  // sum the regions
  float *region = new float[widthPix * lengthPix];
  for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
  {
    region[ptr] = 0;
  }

  int *hit = new int[widthPix * lengthPix];
  for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
  {
    hit[ptr] = 0;
  }

  // wait for the threads to finish
  for (int i = 0; i < threadCount; i++)
  {
    threads[i].join();
  }

  for (int i = 0; i < threadCount; i++)
  {
    for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
    {
      region[ptr] += regions[i][ptr];
      hit[ptr] += hits[i][ptr];
    }
  }

  // norm the region
  for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
  {
    if (hit[ptr] > 0)
    {
      region[ptr] /= hit[ptr];
    }
  }

  return region;
}

extern "C"
{
  float *bp_getRegion(int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float z, float width, float length, float resolution)
  {
    // allocate memory for scans
    int *scansPtr = new int32_t[scanCount * scanLength];
    std::copy(scans, scans + scanCount * scanLength, scansPtr);

    // allocate memory for positions
    float *positionsPtr = new float[scanCount * 4];
    std::copy(positions, positions + scanCount * 4, positionsPtr);

    return getRegion(scansPtr, positionsPtr, scanCount, scanLength, binStart, binEnd, binSize, x, y, z, width, length, resolution);
  }

  int *bp_getDim(float x, float y, float width, float length, float resolution)
  {
    return getDim(x, y, width, length, resolution);
  }
}