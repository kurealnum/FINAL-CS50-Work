// Modifies the volume of an audio file

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Number of bytes in .wav header (specific to .wav files). a wav file has 44 bytes in the header, then 2 bytes for every "sample",
// where each of these samples representes the value of some audio waveform.
const int HEADER_SIZE = 44;

int main(int argc, char *argv[])
{
    // Check command-line arguments
    if (argc != 4)
    {
        printf("Usage: ./volume input.wav output.wav factor\n");
        return 1;
    }

    // Open files and determine scaling factor. Basicaly just make sure the files are correct.
    FILE *input = fopen(argv[1], "r");
    if (input == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    FILE *output = fopen(argv[2], "w");
    if (output == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    float factor = atof(argv[3]);

    // TODO: Copy header from input file to output file (swap values using a temp var?)
    uint8_t header[HEADER_SIZE];
    fread(&header, HEADER_SIZE, 1, input);
    fwrite(&header, HEADER_SIZE, 1, output);

    // TODO: Read samples from input file and write updated data to output file
    int16_t buffer;

    while (fread(&buffer, sizeof(buffer), 1, input))
    {
        buffer *= factor; // buffer acts as a temp variable, which allows us to read and write from it
        fwrite(&buffer, sizeof(buffer), 1, output);
    }

    // Close files (fclose, thats not hard)
    fclose(input);
    fclose(output);
}
