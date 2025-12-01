/**
 * CodeEditor.jsx - Premium Monaco Editor Component
 * Features: VS Code engine, syntax highlighting, autocomplete, themes
 */
import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

export default function CodeEditor({
    code,
    onChange,
    language = 'python',
    readOnly = false,
    onRun,
    onReview,
    onAnalyze
}) {
    const [theme, setTheme] = useState('vs-dark');
    const [fontSize, setFontSize] = useState(14);
    const editorRef = useRef(null);

    const handleEditorDidMount = (editor, monaco) => {
        editorRef.current = editor;

        // Configure Python language features
        monaco.languages.registerCompletionItemProvider('python', {
            provideCompletionItems: () => {
                return {
                    suggestions: [
                        {
                            label: 'def',
                            kind: monaco.languages.CompletionItemKind.Keyword,
                            insertText: 'def ${1:function_name}(${2:args}):\n    ${3:pass}',
                            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                            documentation: 'Define a function'
                        },
                        {
                            label: 'for',
                            kind: monaco.languages.CompletionItemKind.Keyword,
                            insertText: 'for ${1:i} in range(${2:n}):\n    ${3:pass}',
                            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                            documentation: 'For loop'
                        },
                        {
                            label: 'if',
                            kind: monaco.languages.CompletionItemKind.Keyword,
                            insertText: 'if ${1:condition}:\n    ${2:pass}',
                            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                            documentation: 'If statement'
                        }
                    ]
                };
            }
        });
    };

    const handleFormatCode = () => {
        if (editorRef.current) {
            editorRef.current.getAction('editor.action.formatDocument').run();
        }
    };

    const handleCopyCode = () => {
        navigator.clipboard.writeText(code);
    };

    return (
        <div className="code-editor-container">
            {/* Toolbar */}
            <div className="editor-toolbar">
                <div className="toolbar-left">
                    <span className="editor-title">✨ Code Editor</span>
                    <span className="editor-lang">{language.toUpperCase()}</span>
                </div>

                <div className="toolbar-right">
                    {/* Theme Switcher */}
                    <select
                        className="editor-control"
                        value={theme}
                        onChange={(e) => setTheme(e.target.value)}
                    >
                        <option value="vs-dark">🌙 Dark</option>
                        <option value="light">☀️ Light</option>
                        <option value="hc-black">🎨 High Contrast</option>
                    </select>

                    {/* Font Size */}
                    <select
                        className="editor-control"
                        value={fontSize}
                        onChange={(e) => setFontSize(Number(e.target.value))}
                    >
                        <option value={12}>12px</option>
                        <option value={14}>14px</option>
                        <option value={16}>16px</option>
                        <option value={18}>18px</option>
                    </select>

                    {/* Actions */}
                    <button className="editor-btn" onClick={handleFormatCode} title="Format Code">
                        ⚡ Format
                    </button>
                    <button className="editor-btn" onClick={handleCopyCode} title="Copy Code">
                        📋 Copy
                    </button>

                    {/* AI Buttons */}
                    {onReview && (
                        <button className="editor-btn secondary" onClick={onReview} title="AI Code Review">
                            🔍 Review
                        </button>
                    )}
                    {onAnalyze && (
                        <button className="editor-btn secondary" onClick={onAnalyze} title="Deep Analysis">
                            🧠 Analyze
                        </button>
                    )}

                    {onRun && (
                        <button className="editor-btn-primary" onClick={onRun} title="Run Code">
                            ▶️ Run Code
                        </button>
                    )}
                </div>
            </div>

            {/* Monaco Editor */}
            <div className="editor-wrapper">
                <Editor
                    height="100%"
                    language={language}
                    value={code}
                    onChange={onChange}
                    theme={theme}
                    onMount={handleEditorDidMount}
                    options={{
                        fontSize: fontSize,
                        readOnly: readOnly,
                        minimap: { enabled: true },
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        tabSize: 4,
                        insertSpaces: true,
                        wordWrap: 'on',
                        lineNumbers: 'on',
                        glyphMargin: true,
                        folding: true,
                        lineDecorationsWidth: 10,
                        lineNumbersMinChars: 3,
                        renderLineHighlight: 'all',
                        smoothScrolling: true,
                        cursorBlinking: 'smooth',
                        cursorSmoothCaretAnimation: 'on',
                        fontLigatures: true,
                        fontFamily: "'Fira Code', 'Consolas', 'Monaco', monospace",
                        suggestOnTriggerCharacters: true,
                        quickSuggestions: true,
                        parameterHints: { enabled: true },
                        formatOnPaste: true,
                        formatOnType: true
                    }}
                />
            </div>

            {/* Status Bar */}
            <div className="editor-status-bar">
                <span>Lines: {code.split('\n').length}</span>
                <span>Chars: {code.length}</span>
                <span>{readOnly ? '🔒 Read-Only' : '✏️ Editable'}</span>
            </div>
        </div>
    );
}
