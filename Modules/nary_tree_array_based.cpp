#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include <functional>
#include <queue>
#include <cmath>
#include <cassert>

template <typename T>
class ArrayBasedNaryTree {
public:
    struct ArrayNode {
        T data;
        int parent_index;
        int first_child_index;
        int child_count;
        bool is_valid;
        
        ArrayNode() : parent_index(-1), first_child_index(-1), child_count(0), is_valid(false) {}
        ArrayNode(const T& d, int parent = -1) 
            : data(d), parent_index(parent), first_child_index(-1), child_count(0), is_valid(true) {}
    };

private:
    std::vector<ArrayNode> nodes_;
    int root_index_;
    int size_;
    int capacity_;
    
    // For breadth-first layout optimization
    void rebalance_breadth_first() {
        if (root_index_ == -1) return;
        
        std::vector<ArrayNode> new_nodes;
        std::vector<int> old_to_new_mapping(nodes_.size(), -1);
        std::queue<int> bfs_queue;
        
        // BFS traversal to create breadth-first layout
        bfs_queue.push(root_index_);
        old_to_new_mapping[root_index_] = 0;
        new_nodes.push_back(nodes_[root_index_]);
        new_nodes[0].parent_index = -1;
        
        int new_index = 1;
        
        while (!bfs_queue.empty()) {
            int current_old_index = bfs_queue.front();
            bfs_queue.pop();
            int current_new_index = old_to_new_mapping[current_old_index];
            
            // Process children
            int first_child = nodes_[current_old_index].first_child_index;
            if (first_child != -1) {
                new_nodes[current_new_index].first_child_index = new_index;
                
                // Add all children in breadth-first order
                for (int i = 0; i < nodes_[current_old_index].child_count; ++i) {
                    int child_old_index = first_child + i;
                    if (child_old_index < nodes_.size() && nodes_[child_old_index].is_valid) {
                        old_to_new_mapping[child_old_index] = new_index;
                        new_nodes.push_back(nodes_[child_old_index]);
                        new_nodes[new_index].parent_index = current_new_index;
                        bfs_queue.push(child_old_index);
                        new_index++;
                    }
                }
            }
        }
        
        // Replace old layout with breadth-first layout
        nodes_ = std::move(new_nodes);
        root_index_ = 0;
        capacity_ = nodes_.size();
    }

public:
    ArrayBasedNaryTree() : root_index_(-1), size_(0), capacity_(1024) {
        nodes_.reserve(capacity_);
    }
    
    explicit ArrayBasedNaryTree(const T& root_data) : size_(1), capacity_(1024) {
        nodes_.reserve(capacity_);
        nodes_.emplace_back(root_data);
        root_index_ = 0;
    }
    
    // Node access with better locality
    class NodeRef {
    private:
        ArrayBasedNaryTree* tree_;
        int index_;
        
    public:
        NodeRef(ArrayBasedNaryTree* tree, int idx) : tree_(tree), index_(idx) {}
        
        const T& data() const { return tree_->nodes_[index_].data; }
        T& data() { return tree_->nodes_[index_].data; }
        
        int child_count() const { return tree_->nodes_[index_].child_count; }
        
        NodeRef child(int i) const {
            assert(i < child_count());
            int child_idx = tree_->nodes_[index_].first_child_index + i;
            return NodeRef(tree_, child_idx);
        }
        
        NodeRef parent() const {
            int parent_idx = tree_->nodes_[index_].parent_index;
            return NodeRef(tree_, parent_idx);
        }
        
        bool is_valid() const { return index_ >= 0 && index_ < tree_->nodes_.size() && tree_->nodes_[index_].is_valid; }
        
        // Add child with automatic breadth-first optimization
        NodeRef add_child(const T& child_data) {
            int child_index = tree_->add_child_internal(index_, child_data);
            return NodeRef(tree_, child_index);
        }
        
        int get_index() const { return index_; }
    };
    
    NodeRef root() { return NodeRef(this, root_index_); }
    const NodeRef root() const { return NodeRef(const_cast<ArrayBasedNaryTree*>(this), root_index_); }
    
private:
    int add_child_internal(int parent_index, const T& child_data) {
        if (nodes_.size() >= capacity_) {
            capacity_ *= 2;
            nodes_.reserve(capacity_);
        }
        
        // Find insertion point for better locality
        int insert_index = nodes_.size();
        
        // If this is the first child, set up parent's first_child_index
        if (nodes_[parent_index].child_count == 0) {
            // Try to place children consecutively after parent for better cache locality
            if (parent_index + 1 < nodes_.size()) {
                // Find next available consecutive slot
                insert_index = parent_index + 1;
                for (int i = parent_index + 1; i < nodes_.size() && nodes_[i].is_valid; ++i) {
                    insert_index = i + 1;
                }
                
                // If we need to extend the array
                if (insert_index >= nodes_.size()) {
                    nodes_.resize(insert_index + 1);
                }
            }
            nodes_[parent_index].first_child_index = insert_index;
        } else {
            // Place after existing siblings for locality
            int last_sibling = nodes_[parent_index].first_child_index + nodes_[parent_index].child_count - 1;
            insert_index = last_sibling + 1;
            
            if (insert_index >= nodes_.size()) {
                nodes_.resize(insert_index + 1);
            }
        }
        
        // Create the new node
        nodes_[insert_index] = ArrayNode(child_data, parent_index);
        nodes_[parent_index].child_count++;
        size_++;
        
        // Trigger rebalancing for better breadth-first layout periodically
        if (size_ % 100 == 0) {  // Rebalance every 100 nodes
            rebalance_breadth_first();
            // Find the new index after rebalancing
            for (int i = 0; i < nodes_.size(); ++i) {
                if (nodes_[i].is_valid && nodes_[i].data == child_data && nodes_[i].parent_index == parent_index) {
                    return i;
                }
            }
        }
        
        return insert_index;
    }

public:
    // Traversal with better cache locality due to breadth-first layout
    template<typename Func>
    void for_each_breadth_first(Func&& func) {
        if (root_index_ == -1) return;
        
        std::queue<int> queue;
        queue.push(root_index_);
        
        while (!queue.empty()) {
            int current = queue.front();
            queue.pop();
            
            if (current >= 0 && current < nodes_.size() && nodes_[current].is_valid) {
                func(NodeRef(this, current));
                
                // Add children to queue (they're stored consecutively for better locality)
                int first_child = nodes_[current].first_child_index;
                for (int i = 0; i < nodes_[current].child_count; ++i) {
                    queue.push(first_child + i);
                }
            }
        }
    }
    
    // In-order traversal optimized for cache locality
    template<typename Func>
    void for_each_sequential(Func&& func) {
        // Since nodes are stored in breadth-first order, sequential access is cache-friendly
        for (int i = 0; i < nodes_.size(); ++i) {
            if (nodes_[i].is_valid) {
                func(NodeRef(this, i));
            }
        }
    }
    
    // Memory layout analysis
    struct MemoryStats {
        size_t total_memory;
        size_t node_overhead;
        size_t data_memory;
        size_t fragmentation;
        double locality_score;
    };
    
    MemoryStats get_memory_stats() const {
        MemoryStats stats;
        stats.total_memory = nodes_.capacity() * sizeof(ArrayNode);
        stats.node_overhead = nodes_.size() * (sizeof(ArrayNode) - sizeof(T));
        stats.data_memory = nodes_.size() * sizeof(T);
        stats.fragmentation = (nodes_.capacity() - nodes_.size()) * sizeof(ArrayNode);
        
        // Calculate locality score based on breadth-first layout adherence
        stats.locality_score = calculate_locality_score();
        
        return stats;
    }
    
private:
    double calculate_locality_score() const {
        if (size_ <= 1) return 1.0;
        
        double score = 0.0;
        int comparisons = 0;
        
        // Score based on how well children are located near parents
        for (int i = 0; i < nodes_.size(); ++i) {
            if (nodes_[i].is_valid && nodes_[i].child_count > 0) {
                int first_child = nodes_[i].first_child_index;
                
                // Ideal: children immediately follow parent in memory
                double distance_penalty = std::abs(first_child - (i + 1));
                score += 1.0 / (1.0 + distance_penalty / 10.0);  // Penalize distance
                comparisons++;
                
                // Children should be consecutive
                for (int j = 1; j < nodes_[i].child_count; ++j) {
                    if (first_child + j < nodes_.size() && nodes_[first_child + j].is_valid) {
                        score += 1.0;  // Bonus for consecutive children
                    } else {
                        score += 0.5;  // Penalty for gaps
                    }
                    comparisons++;
                }
            }
        }
        
        return comparisons > 0 ? score / comparisons : 1.0;
    }

public:
    int size() const { return size_; }
    bool empty() const { return size_ == 0; }
    
    // Force breadth-first rebalancing for optimal locality
    void optimize_layout() {
        rebalance_breadth_first();
    }
    
    // Debug: print memory layout
    void print_layout() const {
        printf("Array-based N-ary Tree Layout (size=%d):\n", size_);
        for (int i = 0; i < nodes_.size(); ++i) {
            if (nodes_[i].is_valid) {
                printf("  [%d] parent=%d, children=%d@%d\n", 
                       i, nodes_[i].parent_index, nodes_[i].child_count, nodes_[i].first_child_index);
            } else {
                printf("  [%d] <empty>\n", i);
            }
        }
        
        auto stats = get_memory_stats();
        printf("Memory stats: total=%zu bytes, locality_score=%.2f\n", 
               stats.total_memory, stats.locality_score);
    }
};