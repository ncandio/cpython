#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/string.h>
#include "succinct_encoding.h"

/* Forward declaration for node structure */
struct succinct_node {
    unsigned long ino;
    char *name;
    size_t name_len;
    struct succinct_node *parent;
    struct succinct_node **children;
    size_t child_count;
    size_t child_capacity;
    umode_t mode;
    size_t size;
    struct timespec64 mtime;
    struct timespec64 ctime;
    char *data;
};

/* Preorder traversal encoding for kernel */
static void encode_preorder_kernel(struct succinct_node *node, 
                                  unsigned char **bits_ptr, size_t *bit_index,
                                  char ***data_ptr, size_t *data_index)
{
    if (!node)
        return;
    
    /* Set bit to 1 for internal node */
    set_bit_in_array(*bits_ptr, *bit_index, 1);
    (*bit_index)++;
    
    /* Add node name to data array */
    (*data_ptr)[*data_index] = kzalloc(node->name_len + 1, GFP_KERNEL);
    if ((*data_ptr)[*data_index]) {
        strcpy((*data_ptr)[*data_index], node->name);
    }
    (*data_index)++;
    
    /* Encode all children */
    for (size_t i = 0; i < node->child_count; i++) {
        encode_preorder_kernel(node->children[i], bits_ptr, bit_index, data_ptr, data_index);
    }
    
    /* Mark end of children with 0 bit */
    set_bit_in_array(*bits_ptr, *bit_index, 0);
    (*bit_index)++;
}

int succinct_encode_tree_kernel(struct succinct_node *root, struct succinct_encoding *encoding)
{
    if (!root || !encoding)
        return -EINVAL;
    
    /* Count nodes first */
    size_t node_count = 0;
    /* TODO: Add node counting traversal */
    
    /* Estimate bit array size (2n+1 bits) */
    size_t max_bits = node_count * 2 + 1;
    size_t byte_count = (max_bits + 7) / 8;  /* Round up to bytes */
    
    /* Allocate bit array */
    encoding->structure_bits = kzalloc(byte_count, GFP_KERNEL);
    if (!encoding->structure_bits)
        return -ENOMEM;
    
    /* Allocate data array */
    encoding->data_array = kzalloc(node_count * sizeof(char *), GFP_KERNEL);
    if (!encoding->data_array) {
        kfree(encoding->structure_bits);
        return -ENOMEM;
    }
    
    /* Perform encoding */
    size_t bit_index = 0;
    size_t data_index = 0;
    
    encode_preorder_kernel(root, &encoding->structure_bits, &bit_index,
                          &encoding->data_array, &data_index);
    
    encoding->structure_bit_count = bit_index;
    encoding->data_count = data_index;
    encoding->node_count = node_count;
    
    return 0;
}

int succinct_decode_tree_kernel(const struct succinct_encoding *encoding, struct succinct_node **root)
{
    if (!encoding || !root)
        return -EINVAL;
    
    /* TODO: Implement decoding */
    /* This would reconstruct the tree from bit array + data array */
    
    return 0;
}

void succinct_free_encoding(struct succinct_encoding *encoding)
{
    if (!encoding)
        return;
    
    if (encoding->structure_bits) {
        kfree(encoding->structure_bits);
        encoding->structure_bits = NULL;
    }
    
    if (encoding->data_array) {
        for (size_t i = 0; i < encoding->data_count; i++) {
            kfree(encoding->data_array[i]);
        }
        kfree(encoding->data_array);
        encoding->data_array = NULL;
    }
    
    encoding->structure_bit_count = 0;
    encoding->data_count = 0;
    encoding->node_count = 0;
}

size_t succinct_encoding_memory_usage(const struct succinct_encoding *encoding)
{
    if (!encoding)
        return 0;
    
    size_t total = 0;
    
    /* Structure bits */
    total += (encoding->structure_bit_count + 7) / 8;
    
    /* Data array overhead */
    total += encoding->data_count * sizeof(char *);
    
    /* Actual string data */
    for (size_t i = 0; i < encoding->data_count; i++) {
        if (encoding->data_array[i]) {
            total += strlen(encoding->data_array[i]) + 1;
        }
    }
    
    /* Metadata */
    total += sizeof(struct succinct_encoding);
    
    return total;
}