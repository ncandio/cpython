#include <iostream>
#include <vector>
#include <string>

// Simplified array-based N-ary tree for locality testing
template <typename T>
class SimpleArrayNaryTree {
public:
    struct Node {
        T data;
        int parent_index;
        int first_child_index;
        int child_count;
        bool is_valid;
        
        Node() : parent_index(-1), first_child_index(-1), child_count(0), is_valid(false) {}
        Node(const T& d) : data(d), parent_index(-1), first_child_index(-1), child_count(0), is_valid(true) {}
    };

private:
    std::vector<Node> nodes_;
    int root_index_;
    int next_free_index_;

public:
    SimpleArrayNaryTree(const T& root_data) : root_index_(0), next_free_index_(1) {
        nodes_.push_back(Node(root_data));
    }
    
    int add_child(int parent_index, const T& child_data) {
        if (parent_index < 0 || parent_index >= nodes_.size() || !nodes_[parent_index].is_valid) {
            return -1;
        }
        
        int child_index = next_free_index_++;
        nodes_.push_back(Node(child_data));
        nodes_[child_index].parent_index = parent_index;
        
        // Update parent's child info
        if (nodes_[parent_index].child_count == 0) {
            nodes_[parent_index].first_child_index = child_index;
        }
        nodes_[parent_index].child_count++;
        
        return child_index;
    }
    
    void rebalance_breadth_first() {
        if (nodes_.empty()) return;
        
        std::vector<Node> new_nodes;
        std::vector<int> old_to_new(nodes_.size(), -1);
        std::vector<int> queue;
        
        // Start with root
        queue.push_back(root_index_);
        old_to_new[root_index_] = 0;
        new_nodes.push_back(nodes_[root_index_]);
        new_nodes[0].parent_index = -1;
        new_nodes[0].first_child_index = -1;
        new_nodes[0].child_count = 0;
        
        int queue_pos = 0;
        int new_index = 1;
        
        // BFS reordering
        while (queue_pos < queue.size()) {
            int current_old = queue[queue_pos++];
            int current_new = old_to_new[current_old];
            
            // Find children of current node
            std::vector<int> children;
            for (int i = 0; i < nodes_.size(); ++i) {
                if (nodes_[i].is_valid && nodes_[i].parent_index == current_old) {
                    children.push_back(i);
                }
            }
            
            if (!children.empty()) {
                new_nodes[current_new].first_child_index = new_index;
                new_nodes[current_new].child_count = children.size();
                
                for (int child_old : children) {
                    old_to_new[child_old] = new_index;
                    new_nodes.push_back(nodes_[child_old]);
                    new_nodes[new_index].parent_index = current_new;
                    queue.push_back(child_old);
                    new_index++;
                }
            }
        }
        
        nodes_ = std::move(new_nodes);
        next_free_index_ = nodes_.size();
        root_index_ = 0;
    }
    
    void print_tree() {
        std::cout << "Array-based tree (size=" << nodes_.size() << "):\n";
        for (int i = 0; i < nodes_.size(); ++i) {
            if (nodes_[i].is_valid) {
                std::cout << "[" << i << "] '" << nodes_[i].data 
                         << "' parent=" << nodes_[i].parent_index
                         << " children=" << nodes_[i].child_count;
                if (nodes_[i].child_count > 0) {
                    std::cout << "@" << nodes_[i].first_child_index;
                }
                std::cout << "\n";
            }
        }
    }
    
    void traverse_breadth_first() {
        std::cout << "BFS traversal: ";
        std::vector<int> queue;
        queue.push_back(root_index_);
        
        int pos = 0;
        while (pos < queue.size()) {
            int current = queue[pos++];
            std::cout << nodes_[current].data << " ";
            
            // Add children
            int first_child = nodes_[current].first_child_index;
            for (int i = 0; i < nodes_[current].child_count; ++i) {
                if (first_child + i < nodes_.size()) {
                    queue.push_back(first_child + i);
                }
            }
        }
        std::cout << "\n";
    }
    
    double calculate_locality_score() {
        double score = 0.0;
        int comparisons = 0;
        
        for (int i = 0; i < nodes_.size(); ++i) {
            if (nodes_[i].is_valid && nodes_[i].child_count > 0) {
                int first_child = nodes_[i].first_child_index;
                
                // Score based on distance from parent to first child
                double distance = std::abs(first_child - i);
                score += 1.0 / (1.0 + distance / 10.0);
                comparisons++;
                
                // Score consecutive children
                for (int j = 1; j < nodes_[i].child_count; ++j) {
                    if (first_child + j < nodes_.size() && nodes_[first_child + j].is_valid) {
                        score += 1.0;
                    }
                    comparisons++;
                }
            }
        }
        
        return comparisons > 0 ? score / comparisons : 1.0;
    }
    
    size_t size() const { return nodes_.size(); }
};

int main() {
    std::cout << "Simple Array-Based N-ary Tree Locality Test\n";
    std::cout << std::string(50, '=') << '\n';
    
    // Create tree
    SimpleArrayNaryTree<std::string> tree("root");
    
    // Add some structure
    int child1 = tree.add_child(0, "child1");
    int child2 = tree.add_child(0, "child2");
    int child3 = tree.add_child(0, "child3");
    
    tree.add_child(child1, "grandchild1");
    tree.add_child(child1, "grandchild2");
    tree.add_child(child2, "grandchild3");
    
    std::cout << "Initial tree layout:\n";
    tree.print_tree();
    
    std::cout << "\nLocality score before optimization: " 
              << tree.calculate_locality_score() << "\n";
    
    tree.traverse_breadth_first();
    
    std::cout << "\nOptimizing for breadth-first layout...\n";
    tree.rebalance_breadth_first();
    
    std::cout << "\nOptimized tree layout:\n";
    tree.print_tree();
    
    std::cout << "\nLocality score after optimization: " 
              << tree.calculate_locality_score() << "\n";
    
    tree.traverse_breadth_first();
    
    std::cout << "\nBenefits of array-based breadth-first storage:\n";
    std::cout << "• Children are stored consecutively near parents\n";
    std::cout << "• Better CPU cache utilization\n";
    std::cout << "• Reduced pointer chasing overhead\n";
    std::cout << "• More predictable memory access patterns\n";
    std::cout << "• Potential for SIMD optimizations\n";
    
    return 0;
}