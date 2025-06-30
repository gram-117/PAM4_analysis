// Purpose: simulate halfrate PRBS7 sequence as seen in metarock schematics
#include <iostream>
#include <vector>
#include <iomanip>
#include <fstream>
#include <filesystem>

static const int SEQ_SIZE = 127 * 3;


int main() {
     // Get current directory (PAM4)
     std::filesystem::path current_dir = std::filesystem::current_path();

     // Go up one level to lbl/, then into output/
     std::filesystem::path output_path = current_dir.parent_path() / "output" / "prbs7.txt";
 
     // Create output/ directory if it doesn't exist
     std::filesystem::create_directories(output_path.parent_path());
 
     // Open file for writing
     std::ofstream outputFile(output_path);
     if (!outputFile.is_open()) {
         std::cerr << "Failed to open: " << output_path << std::endl;
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

        // write out
        outputFile << outBuffer[2] << bitArr[7];

        // just buffer prbs7 out
        // outputFile2 << outBuffer[2];

        // just prbs7 out
        // outputFile2 << outBuffer[7];

        // xor bit 1 and 6 to get new bit 0
        int newBit = bitArr[1] ^ bitArr[7];
        int newBitBuff = bitArr[2] ^ bitArr[4];
        bitArr[0] = newBit;
        outBuffer[0] = newBitBuff;
        iterations += 1;
    }
    return 0;
}