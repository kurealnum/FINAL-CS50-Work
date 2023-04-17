import sys, csv


def main():

    # TODO: Check for command-line usage
    if len(sys.argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt")

    # TODO: Read database file into a variable
    csv_hashmap = {}
    csvfile = csv.reader(open(sys.argv[1], "r"))

    #skip over the headers, save the headers as a list, then remove the "names" element
    headers = next(csvfile)
    headers.pop(0)


    for row in csvfile:
        csv_hashmap[str(row[0])] = [int(dna_strand) for dna_strand in row[1:]]


    # TODO: Read DNA sequence file into a variable
    with open(sys.argv[2], "r") as file:
        dna_sequence = file.read()

    # TODO: Find longest match of each STR in DNA sequence
    repeat_hashmap = {}
    for row in headers:
        repeat_hashmap[row] = longest_match(dna_sequence, row)

    # TODO: Check database for matching profiles
    for person in csv_hashmap:
        if list(repeat_hashmap.values()) == csv_hashmap[person]:
           print(person)
           return


    print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
