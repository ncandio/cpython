
#include "linux_filesystem_narytree.cpp"
#include <iostream>
#include <chrono>
#include <vector>
#include <random>
#include <thread>
#include <atomic>

using namespace std::chrono;

class TestFilesystemEntry {
public:
    std::string path;
    uint64_t size;
    uint32_t inode;
    
    TestFilesystemEntry(const std::string& p = "", uint64_t s = 0, uint32_t i = 0)
        : path(p), size(s), inode(i) {}
};

// Performance test results structure
struct TestResults {
    double insert_time_ms;
    double search_time_ms;
    double bulk_insert_time_ms;
    double rcu_read_time_ms;
    size_t memory_usage_bytes;
    double page_utilization;
    size_t simd_search_results;
    double directory_listing_time_ms;
    size_t cache_line_efficiency;
};

TestResults run_filesystem_performance_test(size_t num_entries) {
    LinuxFilesystemNaryTree<TestFilesystemEntry*> tree(64, 0); // NUMA node 0
    TestResults results = {};
    
    std::vector<TestFilesystemEntry> entries;
    entries.reserve(num_entries);
    
    // Generate filesystem-like test data
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint32_t> inode_dist(1, 1000000);
    std::uniform_int_distribution<uint64_t> size_dist(0, 1024*1024*1024);
    
    for (size_t i = 0; i < num_entries; ++i) {
        std::string path = "/home/user/file_" + std::to_string(i) + ".txt";
        entries.emplace_back(path, size_dist(gen), inode_dist(gen));
    }
    
    // Test 1: Individual insertions
    auto start = high_resolution_clock::now();
    for (size_t i = 0; i < std::min(num_entries, size_t(1000)); ++i) {
        tree.insert_filesystem_entry(&entries[i], entries[i].inode, 
                                    i > 0 ? entries[i-1].inode : 0,
                                    entries[i].path, entries[i].size, 
                                    duration_cast<microseconds>(system_clock::now().time_since_epoch()).count());
    }
    auto end = high_resolution_clock::now();
    results.insert_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    
    // Test 2: Bulk insertion for remaining entries
    if (num_entries > 1000) {
        std::vector<std::tuple<TestFilesystemEntry*, uint32_t, uint32_t, std::string, uint64_t, uint64_t>> bulk_data;
        for (size_t i = 1000; i < num_entries; ++i) {
            bulk_data.emplace_back(&entries[i], entries[i].inode, entries[i-1].inode,
                                 entries[i].path, entries[i].size, 
                                 duration_cast<microseconds>(system_clock::now().time_since_epoch()).count());
        }
        
        start = high_resolution_clock::now();
        tree.bulk_insert_filesystem_entries(bulk_data);
        end = high_resolution_clock::now();
        results.bulk_insert_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    }
    
    // Test 3: RCU-compatible reads
    start = high_resolution_clock::now();
    for (int i = 0; i < 1000; ++i) {
        auto node = tree.rcu_find_node(entries[i % entries.size()].inode);
        (void)node; // Avoid unused variable warning
    }
    end = high_resolution_clock::now();
    results.rcu_read_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    
    // Test 4: SIMD range search
    start = high_resolution_clock::now();
    auto simd_results = tree.simd_search_range(inode_dist(gen), inode_dist(gen) + 1000);
    end = high_resolution_clock::now();
    results.simd_search_results = simd_results.size();
    
    // Test 5: Directory listing simulation
    start = high_resolution_clock::now();
    for (int i = 0; i < 100; ++i) {
        auto children = tree.get_directory_children(entries[i % entries.size()].inode);
        (void)children;
    }
    end = high_resolution_clock::now();
    results.directory_listing_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    
    // Test 6: Memory statistics
    auto mem_stats = tree.get_filesystem_memory_stats();
    results.memory_usage_bytes = mem_stats.memory_bytes;
    results.page_utilization = mem_stats.page_utilization;
    results.cache_line_efficiency = mem_stats.cache_line_efficiency;
    
    return results;
}

// Concurrent access test
struct ConcurrentTestResults {
    double concurrent_read_time_ms;
    double concurrent_write_time_ms;
    size_t successful_reads;
    size_t successful_writes;
    double rcu_consistency_ratio;
};

ConcurrentTestResults run_concurrent_test(size_t num_threads, size_t operations_per_thread) {
    LinuxFilesystemNaryTree<TestFilesystemEntry*> tree(128, 0);
    ConcurrentTestResults results = {};
    
    // Pre-populate with some data
    std::vector<TestFilesystemEntry> base_entries(1000);
    for (size_t i = 0; i < base_entries.size(); ++i) {
        base_entries[i] = TestFilesystemEntry("/base/file_" + std::to_string(i), 1024, i + 1);
        tree.insert_filesystem_entry(&base_entries[i], base_entries[i].inode, 0,
                                    base_entries[i].path, base_entries[i].size,
                                    duration_cast<microseconds>(system_clock::now().time_since_epoch()).count());
    }
    
    std::atomic<size_t> read_count(0);
    std::atomic<size_t> write_count(0);
    std::atomic<size_t> consistent_reads(0);
    
    auto reader_thread = [&]() {
        for (size_t i = 0; i < operations_per_thread; ++i) {
            auto node = tree.rcu_find_node((i % 1000) + 1);
            if (node) {
                read_count.fetch_add(1);
                if (node->inode_number == ((i % 1000) + 1)) {
                    consistent_reads.fetch_add(1);
                }
            }
        }
    };
    
    auto writer_thread = [&]() {
        std::vector<TestFilesystemEntry> writer_entries(operations_per_thread);
        for (size_t i = 0; i < operations_per_thread; ++i) {
            writer_entries[i] = TestFilesystemEntry("/writer/file_" + std::to_string(i), 2048, 10000 + i);
            bool success = tree.insert_filesystem_entry(&writer_entries[i], writer_entries[i].inode, 1,
                                                       writer_entries[i].path, writer_entries[i].size,
                                                       duration_cast<microseconds>(system_clock::now().time_since_epoch()).count());
            if (success) {
                write_count.fetch_add(1);
            }
        }
    };
    
    // Start concurrent operations
    std::vector<std::thread> readers, writers;
    
    auto start = high_resolution_clock::now();
    
    // Launch reader threads
    for (size_t i = 0; i < num_threads / 2; ++i) {
        readers.emplace_back(reader_thread);
    }
    
    // Launch writer threads
    for (size_t i = 0; i < num_threads / 2; ++i) {
        writers.emplace_back(writer_thread);
    }
    
    // Wait for completion
    for (auto& t : readers) t.join();
    for (auto& t : writers) t.join();
    
    auto end = high_resolution_clock::now();
    double total_time_ms = duration_cast<microseconds>(end - start).count() / 1000.0;
    
    results.concurrent_read_time_ms = total_time_ms;
    results.concurrent_write_time_ms = total_time_ms;
    results.successful_reads = read_count.load();
    results.successful_writes = write_count.load();
    results.rcu_consistency_ratio = static_cast<double>(consistent_reads.load()) / read_count.load();
    
    return results;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <test_type> [params...]\n";
        std::cerr << "test_type: performance, concurrent, scalability\n";
        return 1;
    }
    
    std::string test_type = argv[1];
    
    if (test_type == "performance") {
        size_t num_entries = argc > 2 ? std::atoll(argv[2]) : 10000;
        std::cout << "Running performance test with " << num_entries << " entries...\n";
        
        auto results = run_filesystem_performance_test(num_entries);
        
        std::cout << "{\n";
        std::cout << "  \"insert_time_ms\": " << results.insert_time_ms << ",\n";
        std::cout << "  \"search_time_ms\": " << results.search_time_ms << ",\n";
        std::cout << "  \"bulk_insert_time_ms\": " << results.bulk_insert_time_ms << ",\n";
        std::cout << "  \"rcu_read_time_ms\": " << results.rcu_read_time_ms << ",\n";
        std::cout << "  \"memory_usage_bytes\": " << results.memory_usage_bytes << ",\n";
        std::cout << "  \"page_utilization\": " << results.page_utilization << ",\n";
        std::cout << "  \"simd_search_results\": " << results.simd_search_results << ",\n";
        std::cout << "  \"directory_listing_time_ms\": " << results.directory_listing_time_ms << ",\n";
        std::cout << "  \"cache_line_efficiency\": " << results.cache_line_efficiency << "\n";
        std::cout << "}\n";
        
    } else if (test_type == "concurrent") {
        size_t num_threads = argc > 2 ? std::atoll(argv[2]) : 8;
        size_t ops_per_thread = argc > 3 ? std::atoll(argv[3]) : 1000;
        
        std::cout << "Running concurrent test with " << num_threads << " threads, " 
                  << ops_per_thread << " ops/thread...\n";
        
        auto results = run_concurrent_test(num_threads, ops_per_thread);
        
        std::cout << "{\n";
        std::cout << "  \"concurrent_read_time_ms\": " << results.concurrent_read_time_ms << ",\n";
        std::cout << "  \"concurrent_write_time_ms\": " << results.concurrent_write_time_ms << ",\n";
        std::cout << "  \"successful_reads\": " << results.successful_reads << ",\n";
        std::cout << "  \"successful_writes\": " << results.successful_writes << ",\n";
        std::cout << "  \"rcu_consistency_ratio\": " << results.rcu_consistency_ratio << "\n";
        std::cout << "}\n";
        
    } else if (test_type == "scalability") {
        std::cout << "Running scalability test...\n";
        std::cout << "[\n";
        
        bool first = true;
        for (size_t size : {1000, 10000, 50000, 100000, 500000, 1000000}) {
            if (!first) std::cout << ",\n";
            first = false;
            
            auto results = run_filesystem_performance_test(size);
            std::cout << "  {\n";
            std::cout << "    \"entries\": " << size << ",\n";
            std::cout << "    \"memory_bytes\": " << results.memory_usage_bytes << ",\n";
            std::cout << "    \"memory_per_entry\": " << (double)results.memory_usage_bytes / size << ",\n";
            std::cout << "    \"page_utilization\": " << results.page_utilization << ",\n";
            std::cout << "    \"bulk_insert_time_ms\": " << results.bulk_insert_time_ms << ",\n";
            std::cout << "    \"rcu_read_time_ms\": " << results.rcu_read_time_ms << "\n";
            std::cout << "  }";
        }
        
        std::cout << "\n]\n";
    }
    
    return 0;
}
