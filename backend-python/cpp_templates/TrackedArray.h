#ifndef TRACKED_ARRAY_H
#define TRACKED_ARRAY_H

#include <vector>
#include <string>
#include <iostream>
#include <sstream>

using namespace std;

class TrackedArray {
private:
    vector<int> data;
    vector<string> trace_steps;
    
    void record(string action, vector<int> highlights = {}) {
        stringstream ss;
        
        ss << "{";
        ss << "\"data\":[";
        for (size_t i = 0; i < data.size(); i++) {
            ss << data[i];
            if (i < data.size() - 1) ss << ",";
        }
        ss << "],";
        
        ss << "\"highlights\":[";
        for (size_t i = 0; i < highlights.size(); i++) {
            ss << highlights[i];
            if (i < highlights.size() - 1) ss << ",";
        }
        ss << "],";
        
        ss << "\"action\":\"" << action << "\"";
        ss << "}";
        
        trace_steps.push_back(ss.str());
    }
    
public:
    TrackedArray(const vector<int>& initial_data) : data(initial_data) {
        record("Initial array");
    }
    
    int size() const {
        return data.size();
    }
    
    // Get - silent
    int get(size_t index) {
        if (index >= data.size()) return -1;
        return data[index];
    }
    
    // Set - record it
    void set(size_t index, int value) {
        if (index >= data.size()) return;
        
        stringstream action;
        action << "Set arr[" << index << "] = " << value;
        record(action.str(), {(int)index});
        
        data[index] = value;
    }
    
    // Swap - record it
    void swap(size_t i, size_t j) {
        if (i >= data.size() || j >= data.size()) return;
        
        stringstream action;
        action << "Swap arr[" << i << "] ↔ arr[" << j << "]";
        record(action.str(), {(int)i, (int)j});
        
        int temp = data[i];
        data[i] = data[j];
        data[j] = temp;
    }
    
    // Insert - record it
    void insert(size_t index, int value) {
        if (index > data.size()) return;
        
        stringstream action;
        action << "Insert " << value << " at index " << index;
        record(action.str(), {(int)index});
        
        data.insert(data.begin() + index, value);
    }
    
    // Erase - record it
    void erase(size_t index) {
        if (index >= data.size()) return;
        
        stringstream action;
        action << "Delete arr[" << index << "]";
        record(action.str(), {(int)index});
        
        data.erase(data.begin() + index);
    }
    
    void print_trace() {
        // Add final "Complete" state showing result
        record("✓ Sorting complete!");
        
        cout << "{\"trace\":[";
        for (size_t i = 0; i < trace_steps.size(); i++) {
            cout << trace_steps[i];
            if (i < trace_steps.size() - 1) cout << ",";
        }
        cout << "]}";
    }
};

#endif
