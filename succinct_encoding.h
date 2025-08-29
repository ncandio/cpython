#ifndef SUCCINCT_ENCODING_H
#define SUCCINCT_ENCODING_H

#include <linux/types.h>

/* Succinct encoding structure for kernel use */
struct succinct_encoding {
    unsigned char *structure_bits;  /* Packed bit array */
    size_t structure_bit_count;     /* Number of structure bits */
    char **data_array;              /* Linear array of node names/data */
    size_t data_count;              /* Number of data elements */
    size_t node_count;              /* Total number of nodes */
};

/* Succinct encoding API */
int succinct_encode_tree_kernel(struct succinct_node *root, struct succinct_encoding *encoding);
int succinct_decode_tree_kernel(const struct succinct_encoding *encoding, struct succinct_node **root);
void succinct_free_encoding(struct succinct_encoding *encoding);
size_t succinct_encoding_memory_usage(const struct succinct_encoding *encoding);

/* Helper functions */
static inline void set_bit_in_array(unsigned char *bits, size_t bit_index, int value)
{
    size_t byte_index = bit_index / 8;
    size_t bit_offset = bit_index % 8;
    
    if (value) {
        bits[byte_index] |= (1 << bit_offset);
    } else {
        bits[byte_index] &= ~(1 << bit_offset);
    }
}

static inline int get_bit_from_array(const unsigned char *bits, size_t bit_index)
{
    size_t byte_index = bit_index / 8;
    size_t bit_offset = bit_index % 8;
    
    return (bits[byte_index] >> bit_offset) & 1;
}

#endif /* SUCCINCT_ENCODING_H */