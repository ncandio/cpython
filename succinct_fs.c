#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/pagemap.h>
#include <linux/highmem.h>
#include <linux/time.h>
#include <linux/string.h>
#include <linux/backing-dev.h>
#include <linux/ramfs.h>
#include <linux/sched.h>
#include <linux/parser.h>
#include <linux/magic.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include "succinct_encoding.h"

#define SUCCINCT_FS_MAGIC 0x53434E54  /* "SCNT" */

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Succinct Filesystem Experiment");
MODULE_DESCRIPTION("N-ary Tree Succinct Filesystem");
MODULE_VERSION("1.0");

/* Succinct N-ary Tree Node Structure */
struct succinct_node {
    unsigned long ino;          /* Inode number */
    char *name;                 /* File/directory name */
    size_t name_len;           /* Name length */
    struct succinct_node *parent;
    struct succinct_node **children;
    size_t child_count;
    size_t child_capacity;
    umode_t mode;              /* File mode */
    size_t size;               /* File size */
    struct timespec64 mtime;
    struct timespec64 ctime;
    char *data;                /* File content for regular files */
};

/* Succinct Filesystem Superblock Info */
struct succinct_sb_info {
    struct succinct_node *root_node;
    unsigned long next_ino;
    spinlock_t lock;
    /* Succinct encoding storage */
    unsigned char *structure_bits;
    size_t structure_bit_count;
    char **data_array;
    size_t data_array_count;
    bool is_encoded;           /* Whether tree is in succinct form */
};

/* Forward declarations */
static struct inode *succinct_get_inode(struct super_block *sb, const struct inode *dir, 
                                       umode_t mode, dev_t dev);
static int succinct_mknod(struct user_namespace *mnt_userns, struct inode *dir, 
                         struct dentry *dentry, umode_t mode, dev_t dev);
static int succinct_create(struct user_namespace *mnt_userns, struct inode *dir, 
                          struct dentry *dentry, umode_t mode, bool excl);
static int succinct_mkdir(struct user_namespace *mnt_userns, struct inode *dir, 
                         struct dentry *dentry, umode_t mode);

/* Succinct tree operations */
static struct succinct_node *succinct_alloc_node(const char *name, umode_t mode)
{
    struct succinct_node *node;
    
    node = kzalloc(sizeof(struct succinct_node), GFP_KERNEL);
    if (!node)
        return NULL;
    
    if (name) {
        node->name_len = strlen(name);
        node->name = kzalloc(node->name_len + 1, GFP_KERNEL);
        if (!node->name) {
            kfree(node);
            return NULL;
        }
        strcpy(node->name, name);
    }
    
    node->mode = mode;
    node->child_capacity = 4;  /* Initial capacity */
    node->children = kzalloc(node->child_capacity * sizeof(struct succinct_node *), GFP_KERNEL);
    if (!node->children && node->child_capacity > 0) {
        kfree(node->name);
        kfree(node);
        return NULL;
    }
    
    ktime_get_real_ts64(&node->mtime);
    node->ctime = node->mtime;
    
    return node;
}

static void succinct_free_node(struct succinct_node *node)
{
    if (!node)
        return;
    
    /* Free children recursively */
    for (size_t i = 0; i < node->child_count; i++) {
        succinct_free_node(node->children[i]);
    }
    
    kfree(node->children);
    kfree(node->name);
    kfree(node->data);
    kfree(node);
}

static int succinct_add_child(struct succinct_node *parent, struct succinct_node *child)
{
    if (!parent || !child)
        return -EINVAL;
    
    /* Resize children array if needed */
    if (parent->child_count >= parent->child_capacity) {
        struct succinct_node **new_children;
        size_t new_capacity = parent->child_capacity * 2;
        
        new_children = krealloc(parent->children, 
                               new_capacity * sizeof(struct succinct_node *), 
                               GFP_KERNEL);
        if (!new_children)
            return -ENOMEM;
        
        parent->children = new_children;
        parent->child_capacity = new_capacity;
    }
    
    parent->children[parent->child_count] = child;
    parent->child_count++;
    child->parent = parent;
    
    return 0;
}

/* Succinct encoding operations */
static int succinct_encode_tree(struct succinct_sb_info *sbi)
{
    struct succinct_encoding encoding = {0};
    int ret;
    
    if (!sbi->root_node)
        return -EINVAL;
    
    ret = succinct_encode_tree_kernel(sbi->root_node, &encoding);
    if (ret)
        return ret;
    
    /* Store encoding in superblock */
    sbi->structure_bits = encoding.structure_bits;
    sbi->structure_bit_count = encoding.structure_bit_count;
    sbi->data_array = encoding.data_array;
    sbi->data_array_count = encoding.data_count;
    sbi->is_encoded = true;
    
    printk(KERN_INFO "succinct: Tree encoded to %zu bits + %zu data elements\n",
           encoding.structure_bit_count, encoding.data_count);
    
    return 0;
}

static int succinct_decode_tree(struct succinct_sb_info *sbi)
{
    struct succinct_encoding encoding;
    int ret;
    
    if (!sbi->is_encoded)
        return 0;
    
    encoding.structure_bits = sbi->structure_bits;
    encoding.structure_bit_count = sbi->structure_bit_count;
    encoding.data_array = sbi->data_array;
    encoding.data_count = sbi->data_array_count;
    
    ret = succinct_decode_tree_kernel(&encoding, &sbi->root_node);
    if (ret)
        return ret;
    
    sbi->is_encoded = false;
    
    printk(KERN_INFO "succinct: Tree decoded from succinct format\n");
    
    return 0;
}

/* File operations */
static int succinct_open(struct inode *inode, struct file *filp)
{
    return generic_file_open(inode, filp);
}

static ssize_t succinct_read(struct file *filp, char __user *buf, size_t len, loff_t *ppos)
{
    struct inode *inode = file_inode(filp);
    struct succinct_node *node = inode->i_private;
    
    if (!node || !node->data)
        return 0;
    
    return simple_read_from_buffer(buf, len, ppos, node->data, node->size);
}

static ssize_t succinct_write(struct file *filp, const char __user *buf, size_t len, loff_t *ppos)
{
    struct inode *inode = file_inode(filp);
    struct succinct_node *node = inode->i_private;
    
    if (!node)
        return -ENOENT;
    
    /* Reallocate data buffer if needed */
    if (len > node->size) {
        char *new_data = krealloc(node->data, len, GFP_KERNEL);
        if (!new_data)
            return -ENOMEM;
        node->data = new_data;
    }
    
    if (copy_from_user(node->data, buf, len))
        return -EFAULT;
    
    node->size = len;
    inode->i_size = len;
    ktime_get_real_ts64(&node->mtime);
    
    return len;
}

static const struct file_operations succinct_file_operations = {
    .open = succinct_open,
    .read = succinct_read,
    .write = succinct_write,
    .llseek = generic_file_llseek,
};

/* Directory operations */
static struct dentry *succinct_lookup(struct inode *dir, struct dentry *dentry, unsigned int flags)
{
    struct succinct_node *dir_node = dir->i_private;
    struct succinct_node *child;
    struct inode *inode = NULL;
    
    if (!dir_node)
        return ERR_PTR(-ENOENT);
    
    /* Search for child with matching name */
    for (size_t i = 0; i < dir_node->child_count; i++) {
        child = dir_node->children[i];
        if (child && child->name && 
            strlen(child->name) == dentry->d_name.len &&
            !strncmp(child->name, dentry->d_name.name, dentry->d_name.len)) {
            
            inode = succinct_get_inode(dir->i_sb, dir, child->mode, 0);
            if (inode) {
                inode->i_private = child;
                inode->i_size = child->size;
            }
            break;
        }
    }
    
    return d_splice_alias(inode, dentry);
}

static const struct inode_operations succinct_dir_inode_operations = {
    .lookup = succinct_lookup,
    .create = succinct_create,
    .mkdir = succinct_mkdir,
    .mknod = succinct_mknod,
};

/* Inode operations */
static struct inode *succinct_get_inode(struct super_block *sb, const struct inode *dir, 
                                       umode_t mode, dev_t dev)
{
    struct inode *inode = new_inode(sb);
    struct succinct_sb_info *sbi = sb->s_fs_info;
    
    if (!inode)
        return NULL;
    
    spin_lock(&sbi->lock);
    inode->i_ino = ++sbi->next_ino;
    spin_unlock(&sbi->lock);
    
    inode_init_owner(&init_user_ns, inode, dir, mode);
    inode->i_mapping->a_ops = &ram_aops;
    mapping_set_gfp_mask(inode->i_mapping, GFP_HIGHUSER);
    mapping_set_unevictable(inode->i_mapping);
    
    switch (mode & S_IFMT) {
    case S_IFREG:
        inode->i_op = &ram_file_inode_operations;
        inode->i_fop = &succinct_file_operations;
        break;
    case S_IFDIR:
        inode->i_op = &succinct_dir_inode_operations;
        inode->i_fop = &simple_dir_operations;
        inc_nlink(inode);
        break;
    }
    
    return inode;
}

static int succinct_mknod(struct user_namespace *mnt_userns, struct inode *dir, 
                         struct dentry *dentry, umode_t mode, dev_t dev)
{
    struct inode *inode = succinct_get_inode(dir->i_sb, dir, mode, dev);
    struct succinct_node *dir_node = dir->i_private;
    struct succinct_node *new_node;
    int error = -ENOSPC;
    
    if (!inode)
        return error;
    
    /* Create succinct node */
    new_node = succinct_alloc_node(dentry->d_name.name, mode);
    if (!new_node) {
        iput(inode);
        return -ENOMEM;
    }
    
    new_node->ino = inode->i_ino;
    inode->i_private = new_node;
    
    /* Add to parent directory in succinct tree */
    if (dir_node) {
        error = succinct_add_child(dir_node, new_node);
        if (error) {
            succinct_free_node(new_node);
            iput(inode);
            return error;
        }
    }
    
    d_instantiate(dentry, inode);
    dget(dentry);
    
    return 0;
}

static int succinct_create(struct user_namespace *mnt_userns, struct inode *dir, 
                          struct dentry *dentry, umode_t mode, bool excl)
{
    return succinct_mknod(mnt_userns, dir, dentry, mode | S_IFREG, 0);
}

static int succinct_mkdir(struct user_namespace *mnt_userns, struct inode *dir, 
                         struct dentry *dentry, umode_t mode)
{
    return succinct_mknod(mnt_userns, dir, dentry, mode | S_IFDIR, 0);
}

/* Superblock operations */
static void succinct_put_super(struct super_block *sb)
{
    struct succinct_sb_info *sbi = sb->s_fs_info;
    
    if (sbi) {
        succinct_free_node(sbi->root_node);
        kfree(sbi->structure_bits);
        kfree(sbi->data_array);
        kfree(sbi);
    }
}

static const struct super_operations succinct_ops = {
    .put_super = succinct_put_super,
    .statfs = simple_statfs,
};

/* Mount operations */
static int succinct_fill_super(struct super_block *sb, void *data, int silent)
{
    struct succinct_sb_info *sbi;
    struct inode *inode;
    struct succinct_node *root_node;
    
    /* Initialize superblock */
    sb->s_maxbytes = MAX_LFS_FILESIZE;
    sb->s_blocksize = PAGE_SIZE;
    sb->s_blocksize_bits = PAGE_SHIFT;
    sb->s_magic = SUCCINCT_FS_MAGIC;
    sb->s_op = &succinct_ops;
    sb->s_time_gran = 1;
    
    /* Allocate filesystem private data */
    sbi = kzalloc(sizeof(struct succinct_sb_info), GFP_KERNEL);
    if (!sbi)
        return -ENOMEM;
    
    spin_lock_init(&sbi->lock);
    sbi->next_ino = 1;
    sb->s_fs_info = sbi;
    
    /* Create root directory node in succinct tree */
    root_node = succinct_alloc_node("/", S_IFDIR | 0755);
    if (!root_node) {
        kfree(sbi);
        return -ENOMEM;
    }
    
    root_node->ino = 1;
    sbi->root_node = root_node;
    
    /* Create root inode */
    inode = succinct_get_inode(sb, NULL, S_IFDIR | 0755, 0);
    if (!inode) {
        succinct_free_node(root_node);
        kfree(sbi);
        return -ENOMEM;
    }
    
    inode->i_ino = 1;
    inode->i_private = root_node;
    sb->s_root = d_make_root(inode);
    if (!sb->s_root) {
        succinct_free_node(root_node);
        kfree(sbi);
        return -ENOMEM;
    }
    
    return 0;
}

static struct dentry *succinct_mount(struct file_system_type *fs_type, int flags,
                                    const char *dev_name, void *data)
{
    return mount_nodev(fs_type, flags, data, succinct_fill_super);
}

static void succinct_kill_sb(struct super_block *sb)
{
    kill_litter_super(sb);
}

/* Filesystem type definition */
static struct file_system_type succinct_fs_type = {
    .name = "succinct",
    .mount = succinct_mount,
    .kill_sb = succinct_kill_sb,
    .fs_flags = FS_USERNS_MOUNT,
};

/* Module initialization */
static int __init succinct_init(void)
{
    int ret;
    
    ret = register_filesystem(&succinct_fs_type);
    if (ret) {
        printk(KERN_ERR "succinct: Failed to register filesystem\n");
        return ret;
    }
    
    printk(KERN_INFO "succinct: Succinct N-ary Tree Filesystem registered\n");
    return 0;
}

static void __exit succinct_exit(void)
{
    unregister_filesystem(&succinct_fs_type);
    printk(KERN_INFO "succinct: Filesystem unregistered\n");
}

module_init(succinct_init);
module_exit(succinct_exit);