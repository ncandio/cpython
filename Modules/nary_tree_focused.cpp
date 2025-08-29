#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include <functional>
#include <queue>

template <typename T>
class FocusedNaryTree {
public:
    // Array-based node for locality
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
    
    // Succinct encoding that preserves N-ary structure
    struct SuccinctEncoding {
        std::vector<bool> structure_bits;  // 1=node, 0=end_of_children
        std::vector<T> data_array;         // Node data in preorder
        size_t node_count;
        
        SuccinctEncoding() : node_count(0) {}
        
        size_t memory_usage() const {
            size_t bit_bytes = (structure_bits.size() + 7) / 8;
            size_t data_bytes = data_array.size() * sizeof(T);
            return bit_bytes + data_bytes;
        }
    };

private:
    std::vector<ArrayNode> nodes_;
    int root_index_;
    int size_;
    int operations_since_balance_;
    static const int LAZY_BALANCE_THRESHOLD = 100;

public:
    explicit FocusedNaryTree(const T& root_data) 
        : root_index_(0), size_(1), operations_since_balance_(0) {
        nodes_.push_back(ArrayNode(root_data));
    }
    
    class NodeRef {
    private:
        FocusedNaryTree* tree_;
        int index_;
        
    public:
        NodeRef(FocusedNaryTree* tree, int idx) : tree_(tree), index_(idx) {}
        
        const T& data() const { return tree_->nodes_[index_].data; }
        T& data() { return tree_->nodes_[index_].data; }
        
        int child_count() const { return tree_->nodes_[index_].child_count; }
        
        NodeRef child(int i) const {
            int child_idx = tree_->nodes_[index_].first_child_index + i;
            return NodeRef(tree_, child_idx);
        }
        
        NodeRef add_child(const T& child_data) {
            return tree_->add_child_internal(index_, child_data);
        }
        
        bool is_valid() const {
            return index_ >= 0 && index_ < tree_->nodes_.size() && tree_->nodes_[index_].is_valid;
        }
    };
    
    NodeRef root() { return NodeRef(this, root_index_); }

private:
    NodeRef add_child_internal(int parent_index, const T& child_data) {
        operations_since_balance_++;
        
        int child_index = nodes_.size();
        nodes_.push_back(ArrayNode(child_data, parent_index));
        
        // Update parent's child info
        if (nodes_[parent_index].child_count == 0) {
            nodes_[parent_index].first_child_index = child_index;
        }
        nodes_[parent_index].child_count++;
        size_++;
        
        // Lazy balancing policy
        if (operations_since_balance_ >= LAZY_BALANCE_THRESHOLD) {
            rebalance_for_locality();
        }
        
        return NodeRef(this, child_index);
    }
    
    // Lazy balancing for locality improvement
    void rebalance_for_locality() {
        if (nodes_.empty()) return;
        
        std::vector<ArrayNode> new_nodes;
        std::vector<int> old_to_new(nodes_.size(), -1);
        std::queue<int> queue;
        
        // Breadth-first reordering for better cache locality
        queue.push(root_index_);
        old_to_new[root_index_] = 0;
        new_nodes.push_back(nodes_[root_index_]);
        new_nodes[0].parent_index = -1;
        new_nodes[0].first_child_index = -1;
        new_nodes[0].child_count = 0;
        
        int new_index = 1;
        
        while (!queue.empty()) {
            int current_old = queue.front();
            queue.pop();
            int current_new = old_to_new[current_old];
            
            // Find all children - preserves N-ary structure
            std::vector<int> children;
            for (int i = 0; i < nodes_.size(); ++i) {
                if (nodes_[i].is_valid && nodes_[i].parent_index == current_old) {
                    children.push_back(i);
                }
            }
            
            if (!children.empty()) {
                new_nodes[current_new].first_child_index = new_index;
                new_nodes[current_new].child_count = children.size();
                
                // Add all N children consecutively for locality
                for (int child_old : children) {
                    old_to_new[child_old] = new_index;
                    new_nodes.push_back(nodes_[child_old]);
                    new_nodes[new_index].parent_index = current_new;
                    queue.push(child_old);
                    new_index++;
                }
            }
        }
        
        nodes_ = std::move(new_nodes);
        root_index_ = 0;
        operations_since_balance_ = 0;
    }

public:
    // Succinct encoding that preserves N-ary structure
    SuccinctEncoding encode_succinct() const {
        SuccinctEncoding encoding;
        if (root_index_ < 0) return encoding;
        
        encode_succinct_preorder(root_index_, encoding.structure_bits, encoding.data_array);
        encoding.node_count = size_;
        
        return encoding;
    }

private:
    // Preorder encoding preserving N-ary branching
    void encode_succinct_preorder(int node_index, std::vector<bool>& structure, std::vector<T>& data) const {
        if (node_index < 0 || node_index >= nodes_.size() || !nodes_[node_index].is_valid) {
            return;
        }
        
        structure.push_back(true); // Node marker
        data.push_back(nodes_[node_index].data);
        
        // Encode ALL children (preserves N-ary structure)
        int first_child = nodes_[node_index].first_child_index;
        for (int i = 0; i < nodes_[node_index].child_count; ++i) {
            if (first_child + i < nodes_.size()) {
                encode_succinct_preorder(first_child + i, structure, data);
            }
        }
        
        structure.push_back(false); // End of this node's children
    }

public:
    // Locality analysis
    double calculate_locality_score() const {
        if (nodes_.empty()) return 1.0;
        
        double score = 0.0;
        int comparisons = 0;
        
        for (int i = 0; i < nodes_.size(); ++i) {
            if (nodes_[i].is_valid && nodes_[i].child_count > 0) {
                int first_child = nodes_[i].first_child_index;
                
                // Better score when children are close to parent
                double distance = std::abs(first_child - i);
                score += 1.0 / (1.0 + distance / 10.0);
                comparisons++;
                
                // Better score when children are consecutive
                for (int j = 1; j < nodes_[i].child_count; ++j) {
                    if (first_child + j < nodes_.size() && nodes_[first_child + j].is_valid) {
                        score += 1.0; // Consecutive children
                    } else {
                        score += 0.5; // Gap in children
                    }
                    comparisons++;
                }
            }
        }
        
        return comparisons > 0 ? score / comparisons : 1.0;
    }
    
    // Traversal with good locality
    template<typename Func>
    void for_each_breadth_first(Func&& func) {
        std::queue<int> queue;
        queue.push(root_index_);
        
        while (!queue.empty()) {
            int current = queue.front();
            queue.pop();
            
            if (current >= 0 && current < nodes_.size() && nodes_[current].is_valid) {
                func(NodeRef(this, current));
                
                // Add all N children
                int first_child = nodes_[current].first_child_index;
                for (int i = 0; i < nodes_[current].child_count; ++i) {
                    queue.push(first_child + i);
                }
            }
        }
    }
    
    size_t size() const { return size_; }
    bool empty() const { return size_ == 0; }
    
    // Force lazy rebalancing
    void force_rebalance() {
        rebalance_for_locality();
    }
    
    void print_stats() const {
        auto succinct = encode_succinct();
        
        std::cout << "Focused N-ary Tree Stats:\n";
        std::cout << "Size: " << size_ << " nodes\n";
        std::cout << "Memory: " << (nodes_.size() * sizeof(ArrayNode)) / 1024 << " KB\n";
        std::cout << "Locality score: " << calculate_locality_score() << "/1.0\n";
        std::cout << "Succinct bits: " << succinct.structure_bits.size() << "\n";
        std::cout << "Succinct memory: " << succinct.memory_usage() / 1024 << " KB\n";
        std::cout << "Operations since balance: " << operations_since_balance_ << "\n";
    }
};