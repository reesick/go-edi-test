// Custom Code Editor Component
// Monaco-based code editor with 100-line enforcement and 
// dynamic line highlighting for LineSync AI

import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import './CustomCodeEditor.css';

const DEFAULT_CODE = `#include <iostream>
#include <vector>
using namespace std;

int main() {
    // Example: Bubble Sort
    vector<int> arr = {5, 2, 8, 1, 9};
    int n = arr.size();
    
    for (int i = 0; i < n-1; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                swap(arr[j], arr[j+1]);
            }
        }
    }
    
    // Print sorted array
    for (int x : arr) {
        cout << x << " ";
    }
    
    return 0;
}`;

const CustomCodeEditor = ({
    code,
    onChange,
    highlightedLines = [],
    setupLines = [],
    dimmedLines = [],
    readOnly = false
}) => {
    const editorRef = useRef(null);
    const decorationsRef = useRef([]);

    const handleEditorDidMount = (editor) => {
        editorRef.current = editor;

        // Set up line validation
        editor.onDidChangeModelContent(() => {
            const lineCount = editor.getModel().getLineCount();
            if (lineCount >= 95 && lineCount < 100) {
                console.warn(`Approaching line limit: ${lineCount}/100`);
            } else if (lineCount >= 100) {
                const currentCode = editor.getValue();
                const lines = currentCode.split('\n');
                if (lines.length > 100) {
                    const truncated = lines.slice(0, 100).join('\n');
                    editor.setValue(truncated);
                }
            }
        });
    };

    // Update line decorations when highlights change
    useEffect(() => {
        if (!editorRef.current) return;

        const editor = editorRef.current;
        const monaco = window.monaco;
        if (!monaco) return;

        const newDecorations = [];

        //Highlighted lines (synced with visualization)
        highlightedLines.forEach(lineNum => {
            newDecorations.push({
                range: new monaco.Range(lineNum, 1, lineNum, 1),
                options: {
                    isWholeLine: true,
                    className: 'line-highlight-synced',
                    glyphMarginClassName: 'line-glyph-synced'
                }
            });
        });

        // Setup lines (brief highlight at start)
        setupLines.forEach(lineNum => {
            newDecorations.push({
                range: new monaco.Range(lineNum, 1, lineNum, 1),
                options: {
                    isWholeLine: true,
                    className: 'line-highlight-setup'
                }
            });
        });

        // Dimmed lines (non-visualized)
        dimmedLines.forEach(lineNum => {
            newDecorations.push({
                range: new monaco.Range(lineNum, 1, lineNum, 1),
                options: {
                    isWholeLine: true,
                    className: 'line-dimmed'
                }
            });
        });

        // Apply decorations
        decorationsRef.current = editor.deltaDecorations(
            decorationsRef.current,
            newDecorations
        );
    }, [highlightedLines, setupLines, dimmedLines]);

    const options = {
        selectOnLineNumbers: true,
        roundedSelection: false,
        readOnly: readOnly,
        cursorStyle: 'line',
        automaticLayout: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        glyphMargin: true,
        folding: false,
        lineDecorationsWidth: 10,
        lineNumbersMinChars: 3,
        renderLineHighlight: 'all',
        wordWrap: 'off',
        theme: 'vs-dark'
    };

    return (
        <div className="custom-code-editor">
            <div className="editor-header">
                <span className="editor-title">Code Editor</span>
                <span className="line-counter">
                    Lines: {code.split('\n').length}/100
                    {code.split('\n').length >= 95 && (
                        <span className="warning-badge">
                            {100 - code.split('\n').length} remaining
                        </span>
                    )}
                </span>
            </div>
            <Editor
                height="100%"
                defaultLanguage="cpp"
                value={code}
                onChange={onChange}
                onMount={handleEditorDidMount}
                options={options}
            />
        </div>
    );
};

export default CustomCodeEditor;
export { DEFAULT_CODE };
