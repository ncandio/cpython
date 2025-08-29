/**
 * Simplified Linux Filesystem N-ary Tree for Testing
 * Removes atomic operations for basic performance validation
 */

#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include <chrono>
#include <iostream>
#include <random>

using namespace std::chrono;

// Simple filesystem entry for testing
struct TestFilesystemEntry {
    std::string path;
    uint64_t size;
    uint32_t inode;
    
    TestFilesystemEntry(const std::string& p = "", uint64_t s = 0, uint32_t i = 0)
        : path(p), size(s), inode(i) {}
};

// Simplified node structure for testing
struct SimpleFilesystemNode {
    TestFilesystemEntry* data;
    uint32_t parent_idx;
    uint32_t first_child_idx;
    uint32_t inode_number;
    uint32_t hash_value;
    uint16_t child_count;
    uint16_t depth;
    uint64_t size_or_blocks;
    uint64_t timestamp;
    uint64_t version;
    
    SimpleFilesystemNode() : data(nullptr), parent_idx(UINT32_MAX), 
                            first_child_idx(UINT32_MAX), inode_number(0), 
                            hash_value(0), child_count(0), depth(0),
                            size_or_blocks(0), timestamp(0), version(0) {}
};

// Page-aligned storage (4KB pages)
constexpr size_t LINUX_PAGE_SIZE = 4096;
constexpr size_t NODES_PER_PAGE = (LINUX_PAGE_SIZE - 32) / sizeof(SimpleFilesystemNode);

struct SimplePage {
    SimpleFilesystemNode nodes[NODES_PER_PAGE];
    uint32_t used_nodes;
    uint32_t page_id;
    uint64_t reserved[2]; // Padding to page boundary
    
    SimplePage() : used_nodes(0), page_id(0) {
        reserved[0] = reserved[1] = 0;
    }
};

class SimpleLinuxFilesystemTree {
private:
    std::vector<std::unique_ptr<SimplePage>> pages_;
    size_t total_nodes_;
    size_t root_page_id_;
    size_t root_node_idx_;
    
public:
    SimpleLinuxFilesystemTree() : total_nodes_(0), root_page_id_(0), root_node_idx_(UINT32_MAX) {
        allocate_new_page();
    }
    
    SimplePage* allocate_new_page() {
        auto page = std::make_unique<SimplePage>();
        page->page_id = pages_.size();
        SimplePage* page_ptr = page.get();
        pages_.push_back(std::move(page));
        return page_ptr;
    }
    
    bool insert_filesystem_entry(TestFilesystemEntry* data, uint32_t inode_number,
                                 uint32_t parent_inode, uint32_t hash_value,
                                 uint64_t size, uint64_t timestamp) {
        // Find available slot
        SimplePage* target_page = nullptr;
        size_t node_idx = UINT32_MAX;
        
        for (auto& page : pages_) {
            if (page->used_nodes < NODES_PER_PAGE) {
                target_page = page.get();
                node_idx = page->used_nodes++;
                break;
            }
        }
        
        if (!target_page) {
            target_page = allocate_new_page();
            node_idx = target_page->used_nodes++;
        }
        
        // Initialize node
        auto& node = target_page->nodes[node_idx];
        node.data = data;
        node.inode_number = inode_number;
        node.hash_value = hash_value;
        node.size_or_blocks = size;
        node.timestamp = timestamp;
        node.version = 1;
        
        if (root_node_idx_ == UINT32_MAX) {
            root_page_id_ = target_page->page_id;
            root_node_idx_ = node_idx;
        }
        
        total_nodes_++;
        return true;
    }
    
    const SimpleFilesystemNode* find_node(uint32_t inode_number) const {
        for (const auto& page : pages_) {
            for (size_t i = 0; i < page->used_nodes; ++i) {
                if (page->nodes[i].inode_number == inode_number) {
                    return &page->nodes[i];
                }
            }
        }
        return nullptr;
    }
    
    struct MemoryStats {
        size_t total_pages;
        size_t total_nodes;
        size_t memory_bytes;
        double page_utilization;
        double memory_per_entry;
    };
    
    MemoryStats get_memory_stats() const {
        MemoryStats stats;
        stats.total_pages = pages_.size();
        stats.total_nodes = total_nodes_;
        stats.memory_bytes = stats.total_pages * LINUX_PAGE_SIZE;
        
        size_t used_nodes = 0;
        for (const auto& page : pages_) {
            used_nodes += page->used_nodes;
        }
        
        stats.page_utilization = static_cast<double>(used_nodes) / (stats.total_pages * NODES_PER_PAGE);
        stats.memory_per_entry = static_cast<double>(stats.memory_bytes) / used_nodes;
        
        return stats;
    }
    
    void bulk_insert_filesystem_entries(const std::vector<TestFilesystemEntry*>& entries) {
        // Reserve pages based on expected size
        size_t expected_pages = (entries.size() + NODES_PER_PAGE - 1) / NODES_PER_PAGE;
        while (pages_.size() < expected_pages) {
            allocate_new_page();
        }
        
        // Batch insert
        for (size_t i = 0; i < entries.size(); ++i) {
            uint32_t hash = simple_hash(entries[i]->path);
            insert_filesystem_entry(entries[i], entries[i]->inode, 
                                   i > 0 ? entries[i-1]->inode : 0,
                                   hash, entries[i]->size,
                                   duration_cast<microseconds>(system_clock::now().time_since_epoch()).count());
        }
    }
    
private:
    uint32_t simple_hash(const std::string& str) const {
        uint32_t hash = 2166136261u;
        for (char c : str) {
            hash ^= static_cast<uint32_t>(c);
            hash *= 16777619u;
        }
        return hash;
    }
};

// Performance test results
struct TestResults {
    double insert_time_ms;
    double bulk_insert_time_ms;
    double search_time_ms;
    size_t memory_usage_bytes;
    double page_utilization;
    double memory_per_entry;
};

TestResults run_performance_test(size_t num_entries) {
    SimpleLinuxFilesystemTree tree;
    TestResults results = {};
    
    // Generate test data
    std::vector<std::unique_ptr<TestFilesystemEntry>> entries;
    std::vector<TestFilesystemEntry*> entry_ptrs;
    entries.reserve(num_entries);
    entry_ptrs.reserve(num_entries);
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint32_t> inode_dist(1, 1000000);
    std::uniform_int_distribution<uint64_t> size_dist(0, 1024*1024*1024);
    
    for (size_t i = 0; i < num_entries; ++i) {
        std::string path = "/home/user/file_" + std::to_string(i) + ".txt";
        entries.emplace_back(std::make_unique<TestFilesystemEntry>(path, size_dist(gen), inode_dist(gen)));
        entry_ptrs.push_back(entries.back().get());
    }
    
    // Test individual insertions (first 1000)
    auto start = high_resolution_clock::now();
    for (size_t i = 0; i < std::min(num_entries, size_t(1000)); ++i) {
        uint32_t hash = 2166136261u;
        for (char c : entries[i]->path) {
            hash ^= static_cast<uint32_t>(c);
            hash *= 16777619u;
        }
        tree.insert_filesystem_entry(entries[i].get(), entries[i]->inode,
                                    i > 0 ? entries[i-1]->inode : 0, hash,
                                    entries[i]->size, 
                                    duration_cast<microseconds>(system_clock::now().time_since_epoch()).count());
    }
    auto end = high_resolution_clock::now();
    results.insert_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    
    // Test bulk insertion for remaining
    if (num_entries > 1000) {
        std::vector<TestFilesystemEntry*> bulk_entries(entry_ptrs.begin() + 1000, entry_ptrs.end());
        
        start = high_resolution_clock::now();
        tree.bulk_insert_filesystem_entries(bulk_entries);
        end = high_resolution_clock::now();
        results.bulk_insert_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    }
    
    // Test search performance
    start = high_resolution_clock::now();
    for (int i = 0; i < 1000 && i < static_cast<int>(num_entries); ++i) {
        auto node = tree.find_node(entries[i]->inode);
        (void)node; // Avoid unused variable warning
    }
    end = high_resolution_clock::now();
    results.search_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    
    // Get memory statistics
    auto mem_stats = tree.get_memory_stats();
    results.memory_usage_bytes = mem_stats.memory_bytes;
    results.page_utilization = mem_stats.page_utilization;
    results.memory_per_entry = mem_stats.memory_per_entry;
    
    return results;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <test_type> [size]\\n";
        std::cerr << "test_type: performance, scalability\\n";
        return 1;
    }
    
    std::string test_type = argv[1];
    
    if (test_type == "performance") {
        size_t num_entries = argc > 2 ? std::atoll(argv[2]) : 10000;
        
        auto results = run_performance_test(num_entries);
        
        std::cout << "{\\n";
        std::cout << "  \"entries\": " << num_entries << ",\\n";
        std::cout << "  \"insert_time_ms\": " << results.insert_time_ms << ",\\n";
        std::cout << "  \"bulk_insert_time_ms\": " << results.bulk_insert_time_ms << ",\\n";
        std::cout << "  \"search_time_ms\": " << results.search_time_ms << ",\\n";
        std::cout << "  \"memory_usage_bytes\": " << results.memory_usage_bytes << ",\\n";
        std::cout << "  \"page_utilization\": " << results.page_utilization << ",\\n";
        std::cout << "  \"memory_per_entry\": " << results.memory_per_entry << "\\n";
        std::cout << "}\\n";
        
    } else if (test_type == "scalability") {
        std::cout << "[\\n";
        
        bool first = true;
        std::vector<size_t> sizes = {1000, 10000, 50000, 100000, 500000, 1000000};
        
        for (size_t size : sizes) {
            if (!first) std::cout << ",\\n";
            first = false;
            
            auto results = run_performance_test(size);
            
            std::cout << "  {\\n";
            std::cout << "    \"entries\": " << size << ",\\n";
            std::cout << "    \"memory_bytes\": " << results.memory_usage_bytes << ",\\n";
            std::cout << "    \"memory_per_entry\": " << results.memory_per_entry << ",\\n";
            std::cout << "    \"page_utilization\": " << results.page_utilization << ",\\n";
            std::cout << "    \"bulk_insert_time_ms\": " << results.bulk_insert_time_ms << ",\\n";
            std::cout << "    \"search_time_ms\": " << results.search_time_ms << "\\n";
            std::cout << "  }";
        }
        
        std::cout << "\\n]\\n";
    }
    
    return 0;
}