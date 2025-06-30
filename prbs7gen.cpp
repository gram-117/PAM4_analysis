// Purpose: simulate halfrate PRBS7 sequence as seen in metarock schematics
#include <iostream>
#include <vector>
#include <iomanip>
#include <fstream>

static const int SEQ_SIZE = 127 * 3;


int main() {
    std::ofstream outputFile("prbs7.txt");
    if (!outputFile.is_open())  {
        std::cerr << "Error opening output file." << std::endl;
        return 1;
    }

    std::ofstream outputFile2("prbs7buff.txt");
    if (!outputFile.is_open())  {
        std::cerr << "Error opening output file." << std::endl;
        return 1;
    }


    const int bitCount = 8;
    int bitArr[] = {1, 1, 1, 1, 1, 1, 1, 1}; // Initial state of the PRBS7 shift registers
    const int outBufferCount = 3;
    int outBuffer[] = {1, 1, 1};

    int iterations = 0;
    while (iterations < SEQ_SIZE) {
        // shift registers
        for (int i = bitCount - 1; i > 0; i--) {
            bitArr[i] = bitArr[i - 1];
        }
        for (int i = outBufferCount - 1; i > 0; i--) {
            outBuffer[i] = outBuffer[i - 1];
        }

        // write out_msb
        outputFile << outBuffer[2] << bitArr[7];
        outputFile2 << outBuffer[2];
        // xor bit 1 and 6 to get new bit 0
        int newBit = bitArr[1] ^ bitArr[7];
        int newBitBuff = bitArr[2] ^ bitArr[4];
        bitArr[0] = newBit;
        outBuffer[0] = newBitBuff;
        iterations += 1;
    }
    return 0;
}