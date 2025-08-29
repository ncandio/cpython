#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include <functional>
#include <iterator>
#include <stdexcept>
#include <queue>
#include <stack>
#include <type_traits>
#include <immintrin.h> // For SIMD operations

template <typename T>
class HybridArrayNaryTree {
public:
    // Cache-optimized node structure for array storage
    struct CacheOptimizedNode {
        T data;                    // 8 bytes (assuming pointer/primitive)
        uint32_t parent_idx;       // 4 bytes (index into array)
        uint32_t first_child_idx;  // 4 bytes (index of first child)
        uint16_t child_count;      // 2 bytes (number of children)
        uint16_t depth;           // 2 bytes (depth in tree)
        // Total: 20 bytes -> 3 nodes per 64-byte cache line
    } __attribute__((packed));
    
    // Traditional pointer-based node for lower levels
    class PointerNode {
        friend class HybridArrayNaryTree<T>;
    private:
        T data_;
        std::vector<std::unique_ptr<PointerNode>> children_;
        PointerNode* parent_;
        uint32_t array_parent_idx_; // Link back to array portion
        
    public:
        explicit PointerNode(T data, PointerNode* parent = nullptr, uint32_t array_parent = UINT32_MAX) 
            : data_(std::move(data)), parent_(parent), array_parent_idx_(array_parent) {}
        
        ~PointerNode() = default;
        
        // Move and copy semantics
        PointerNode(const PointerNode&) = delete;
        PointerNode& operator=(const PointerNode&) = delete;
        PointerNode(PointerNode&&) = default;
        PointerNode& operator=(PointerNode&&) = default;
        
        // Standard node operations (similar to original implementation)
        const T& data() const noexcept { return data_; }
        T& data() noexcept { return data_; }
        void set_data(T new_data) { data_ = std::move(new_data); }
        
        size_t child_count() const noexcept { return children_.size(); }
        bool is_leaf() const noexcept { return children_.empty(); }
        
        PointerNode& add_child(T child_data) {
            auto child = std::make_unique<PointerNode>(std::move(child_data), this);
            PointerNode* child_ptr = child.get();
            children_.push_back(std::move(child));
            return *child_ptr;
        }
    };

private:
    // Array storage for hot data (top levels)
    std::vector<CacheOptimizedNode> array_storage_;
    size_t array_levels_;           // Number of levels stored in array
    size_t array_node_count_;       // Number of nodes in array storage
    
    // Pointer storage for cold data (bottom levels)
    std::vector<std::unique_ptr<PointerNode>> pointer_roots_; // Roots of pointer subtrees
    
    // Tree parameters
    size_t total_size_;
    size_t max_children_per_node_;
    
    // Performance tuning parameters
    static constexpr size_t DEFAULT_ARRAY_LEVELS = 3;  // Top 3 levels in array
    static constexpr size_t CACHE_LINE_SIZE = 64;
    static constexpr size_t SIMD_WIDTH = 8;  // AVX2: 8 32-bit integers
    static constexpr uint32_t INVALID_INDEX = UINT32_MAX;

public:
    // Constructors
    explicit HybridArrayNaryTree(T root_data, size_t max_children = 3, size_t array_levels = DEFAULT_ARRAY_LEVELS) 
        : array_levels_(array_levels), 
          array_node_count_(1),
          total_size_(1), 
          max_children_per_node_(max_children) {
        
        // Initialize array storage with root
        array_storage_.reserve(calculate_array_capacity());
        array_storage_.emplace_back();
        array_storage_[0].data = std::move(root_data);
        array_storage_[0].parent_idx = INVALID_INDEX;
        array_storage_[0].first_child_idx = INVALID_INDEX;
        array_storage_[0].child_count = 0;
        array_storage_[0].depth = 0;
    }
    
    HybridArrayNaryTree(size_t max_children = 3, size_t array_levels = DEFAULT_ARRAY_LEVELS) 
        : array_levels_(array_levels), 
          array_node_count_(0),
          total_size_(0), 
          max_children_per_node_(max_children) {
        
        array_storage_.reserve(calculate_array_capacity());
    }
    
    // Move semantics
    HybridArrayNaryTree(HybridArrayNaryTree&&) = default;
    HybridArrayNaryTree& operator=(HybridArrayNaryTree&&) = default;
    
    // Delete copy semantics
    HybridArrayNaryTree(const HybridArrayNaryTree&) = delete;
    HybridArrayNaryTree& operator=(const HybridArrayNaryTree&) = delete;
    
    // Basic tree operations
    bool empty() const noexcept { return total_size_ == 0; }
    size_t size() const noexcept { return total_size_; }
    size_t array_size() const noexcept { return array_node_count_; }
    size_t pointer_size() const noexcept { return total_size_ - array_node_count_; }
    
    void set_root(T root_data) {
        clear();
        array_storage_.emplace_back();
        array_storage_[0].data = std::move(root_data);
        array_storage_[0].parent_idx = INVALID_INDEX;
        array_storage_[0].first_child_idx = INVALID_INDEX;
        array_storage_[0].child_count = 0;
        array_storage_[0].depth = 0;
        array_node_count_ = 1;
        total_size_ = 1;
    }
    
    void clear() {
        array_storage_.clear();
        pointer_roots_.clear();
        array_node_count_ = 0;
        total_size_ = 0;
    }
    
    // Enhanced array-based operations
    const T& get_array_node_data(uint32_t index) const {
        if (index >= array_node_count_) {
            throw std::out_of_range("Array node index out of range");
        }
        return array_storage_[index].data;
    }
    
    T& get_array_node_data(uint32_t index) {
        if (index >= array_node_count_) {
            throw std::out_of_range("Array node index out of range");
        }
        return array_storage_[index].data;
    }
    
    // SIMD-optimized search in array portion
    uint32_t simd_search_array_level(uint32_t level_start, uint32_t level_size, const T& target) const {
        static_assert(std::is_integral_v<T> && sizeof(T) == 4, "SIMD search requires 32-bit integer type");
        
        if (level_size == 0) return INVALID_INDEX;
        
        const uint32_t* level_data = reinterpret_cast<const uint32_t*>(&array_storage_[level_start]);
        
        for (uint32_t i = 0; i < level_size; i += SIMD_WIDTH) {
            uint32_t remaining = std::min(SIMD_WIDTH, level_size - i);
            
            if (remaining >= SIMD_WIDTH) {
                __m256i data_vec = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(&level_data[i]));
                __m256i target_vec = _mm256_set1_epi32(static_cast<uint32_t>(target));
                __m256i cmp_result = _mm256_cmpeq_epi32(data_vec, target_vec);
                
                int mask = _mm256_movemask_ps(reinterpret_cast<__m256>(cmp_result));
                if (mask != 0) {
                    return level_start + i + __builtin_ctz(mask);
                }
            } else {
                // Handle remaining elements with scalar operations
                for (uint32_t j = 0; j < remaining; ++j) {
                    if (array_storage_[level_start + i + j].data == target) {
                        return level_start + i + j;
                    }
                }
            }
        }
        return INVALID_INDEX;
    }
    
    // Cache-optimized level-order traversal of array portion
    template<typename Func>
    void for_each_array_levelorder(Func&& func) const {
        // Prefetch next cache line for optimal performance
        for (uint32_t i = 0; i < array_node_count_; ++i) {
            if (i + 3 < array_node_count_) { // Prefetch 3 nodes ahead
                __builtin_prefetch(&array_storage_[i + 3], 0, 3);
            }
            func(array_storage_[i].data);
        }
    }
    
    // Add child to array portion (if space available) or pointer portion
    uint32_t add_child_optimized(uint32_t parent_idx, T child_data) {
        if (parent_idx >= array_node_count_) {
            throw std::out_of_range("Parent index out of range");
        }
        
        auto& parent = array_storage_[parent_idx];
        
        // Check if we can still add to array portion
        if (parent.depth < array_levels_ - 1 && array_node_count_ < calculate_array_capacity()) {
            return add_child_to_array(parent_idx, std::move(child_data));
        } else {
            return add_child_to_pointer_subtree(parent_idx, std::move(child_data));
        }
    }
    
    // Enhanced balancing with hybrid approach
    void balance_tree_hybrid() {
        if (total_size_ <= 1) return;
        
        // Step 1: Collect all data from both array and pointer portions
        std::vector<T> all_data;
        all_data.reserve(total_size_);
        
        // Collect from array portion (already in level-order)
        for (uint32_t i = 0; i < array_node_count_; ++i) {
            all_data.push_back(array_storage_[i].data);
        }
        
        // Collect from pointer portions
        for (const auto& root : pointer_roots_) {
            collect_pointer_subtree_data(root.get(), all_data);
        }
        
        // Step 2: Rebuild with optimal hybrid layout
        rebuild_hybrid_structure(all_data);
    }
    
    // Statistics with hybrid information
    struct HybridTreeStats {
        size_t total_nodes = 0;
        size_t array_nodes = 0;
        size_t pointer_nodes = 0;
        size_t array_levels = 0;
        size_t max_depth = 0;
        double array_hit_ratio = 0.0; // Percentage of operations hitting array portion
        double cache_efficiency = 0.0; // Estimated cache hit rate
        size_t memory_savings_bytes = 0; // Memory saved by hybrid approach
    };
    
    HybridTreeStats get_hybrid_statistics() const {
        HybridTreeStats stats;
        
        stats.total_nodes = total_size_;
        stats.array_nodes = array_node_count_;
        stats.pointer_nodes = total_size_ - array_node_count_;
        stats.array_levels = array_levels_;
        
        // Calculate max depth
        stats.max_depth = calculate_max_depth();
        
        // Estimate array hit ratio (top levels handle most operations)
        double total_array_capacity = calculate_array_capacity();
        stats.array_hit_ratio = (array_node_count_ / total_array_capacity) * 0.8; // 80% of ops hit top levels
        
        // Estimate cache efficiency improvement
        stats.cache_efficiency = 0.95 * (array_node_count_ / static_cast<double>(total_size_)) + 
                               0.7 * (pointer_nodes / static_cast<double>(total_size_));
        
        // Calculate memory savings
        size_t pointer_overhead = pointer_nodes * 48; // 48 bytes overhead per pointer node
        size_t array_overhead = array_node_count_ * 4;  // 4 bytes overhead per array node
        stats.memory_savings_bytes = pointer_overhead - array_overhead;
        
        return stats;
    }

private:
    // Calculate capacity needed for array portion
    size_t calculate_array_capacity() const {
        size_t capacity = 0;
        size_t level_size = 1;
        
        for (size_t level = 0; level < array_levels_; ++level) {
            capacity += level_size;
            level_size *= max_children_per_node_;
        }
        
        return capacity;
    }
    
    // Add child to array portion
    uint32_t add_child_to_array(uint32_t parent_idx, T child_data) {
        auto& parent = array_storage_[parent_idx];
        
        // Find insertion point
        uint32_t child_idx = array_node_count_;
        array_storage_.emplace_back();
        
        auto& child = array_storage_[child_idx];
        child.data = std::move(child_data);
        child.parent_idx = parent_idx;
        child.first_child_idx = INVALID_INDEX;
        child.child_count = 0;
        child.depth = parent.depth + 1;
        
        // Update parent
        if (parent.child_count == 0) {
            parent.first_child_idx = child_idx;
        }
        parent.child_count++;
        
        array_node_count_++;
        total_size_++;
        
        return child_idx;
    }
    
    // Add child to pointer subtree
    uint32_t add_child_to_pointer_subtree(uint32_t array_parent_idx, T child_data) {
        // Find or create pointer subtree root for this array node
        auto subtree_root = find_or_create_pointer_subtree(array_parent_idx);
        
        // Add child to pointer subtree
        subtree_root->add_child(std::move(child_data));
        total_size_++;
        
        return INVALID_INDEX; // Pointer portion doesn't use indices
    }
    
    // Find or create pointer subtree root
    PointerNode* find_or_create_pointer_subtree(uint32_t array_parent_idx) {
        // Check if pointer subtree already exists for this array node
        for (auto& root : pointer_roots_) {
            if (root->array_parent_idx_ == array_parent_idx) {
                return root.get();
            }
        }
        
        // Create new pointer subtree
        auto new_root = std::make_unique<PointerNode>(T{}, nullptr, array_parent_idx);
        PointerNode* root_ptr = new_root.get();
        pointer_roots_.push_back(std::move(new_root));
        
        return root_ptr;
    }
    
    // Collect data from pointer subtree
    void collect_pointer_subtree_data(const PointerNode* node, std::vector<T>& data) const {
        if (!node) return;
        
        data.push_back(node->data());
        
        for (size_t i = 0; i < node->child_count(); ++i) {
            collect_pointer_subtree_data(&node->children_[i], data);
        }
    }
    
    // Rebuild hybrid structure with collected data
    void rebuild_hybrid_structure(const std::vector<T>& data) {
        // Clear current structure
        array_storage_.clear();
        pointer_roots_.clear();
        array_node_count_ = 0;
        
        if (data.empty()) {
            total_size_ = 0;
            return;
        }
        
        // Rebuild array portion first (top levels)
        size_t array_capacity = calculate_array_capacity();
        size_t array_elements = std::min(data.size(), array_capacity);
        
        array_storage_.reserve(array_capacity);
        
        // Build balanced array portion
        build_balanced_array_portion(data, 0, array_elements);
        
        // Build pointer portions for remaining data
        if (data.size() > array_elements) {
            build_pointer_portions(data, array_elements);
        }
        
        total_size_ = data.size();
    }
    
    // Build balanced array portion
    void build_balanced_array_portion(const std::vector<T>& data, size_t start, size_t count) {
        if (count == 0) return;
        
        array_storage_.emplace_back();
        auto& root = array_storage_[0];
        root.data = data[start];
        root.parent_idx = INVALID_INDEX;
        root.first_child_idx = INVALID_INDEX;
        root.child_count = 0;
        root.depth = 0;
        
        array_node_count_ = 1;
        
        // Build remaining levels
        size_t current_start = start + 1;
        build_array_level(data, current_start, count - 1, 0, 1);
    }
    
    // Recursively build array levels
    void build_array_level(const std::vector<T>& data, size_t& data_idx, size_t remaining, 
                          uint32_t parent_level_start, size_t parent_level_size) {
        if (remaining == 0 || array_node_count_ + remaining > calculate_array_capacity()) return;
        
        uint32_t level_start = array_node_count_;
        size_t level_size = 0;
        
        // Add children for each parent in the previous level
        for (size_t parent_offset = 0; parent_offset < parent_level_size && remaining > 0; ++parent_offset) {
            uint32_t parent_idx = parent_level_start + parent_offset;
            auto& parent = array_storage_[parent_idx];
            
            size_t children_to_add = std::min(remaining, max_children_per_node_);
            if (children_to_add == 0) break;
            
            parent.first_child_idx = array_node_count_;
            parent.child_count = static_cast<uint16_t>(children_to_add);
            
            for (size_t child = 0; child < children_to_add && data_idx < data.size(); ++child) {
                array_storage_.emplace_back();
                auto& child_node = array_storage_[array_node_count_];
                
                child_node.data = data[data_idx++];
                child_node.parent_idx = parent_idx;
                child_node.first_child_idx = INVALID_INDEX;
                child_node.child_count = 0;
                child_node.depth = parent.depth + 1;
                
                array_node_count_++;
                level_size++;
                remaining--;
            }
        }
        
        // Recursively build next level if we haven't reached max array levels
        if (level_size > 0 && remaining > 0 && array_storage_[level_start].depth < array_levels_ - 1) {
            build_array_level(data, data_idx, remaining, level_start, level_size);
        }
    }
    
    // Build pointer portions for remaining data
    void build_pointer_portions(const std::vector<T>& data, size_t start_idx) {
        // Implementation would create pointer-based subtrees
        // attached to leaf array nodes
        // ... (implementation details)
    }
    
    // Calculate maximum depth of hybrid tree
    size_t calculate_max_depth() const {
        size_t max_array_depth = 0;
        for (uint32_t i = 0; i < array_node_count_; ++i) {
            max_array_depth = std::max(max_array_depth, static_cast<size_t>(array_storage_[i].depth));
        }
        
        size_t max_pointer_depth = 0;
        for (const auto& root : pointer_roots_) {
            max_pointer_depth = std::max(max_pointer_depth, calculate_pointer_subtree_depth(root.get()));
        }
        
        return max_array_depth + max_pointer_depth + 1;
    }
    
    // Calculate depth of pointer subtree
    size_t calculate_pointer_subtree_depth(const PointerNode* node) const {
        if (!node || node->is_leaf()) return 0;
        
        size_t max_child_depth = 0;
        for (size_t i = 0; i < node->child_count(); ++i) {
            max_child_depth = std::max(max_child_depth, 
                calculate_pointer_subtree_depth(node->children_[i].get()));
        }
        
        return max_child_depth + 1;
    }
};