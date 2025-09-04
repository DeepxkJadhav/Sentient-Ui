// src/App.jsx
import { useState } from 'react';

export default function App() {
  const [task, setTask] = useState('');
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  const runTask = async () => {
    if (!task.trim()) return;
    
    setIsRunning(true);
    setLogs([
      '🚀 sentient-ui activated...',
      `🧠 Using Gemini Pro 1.5`,
      `📦 Task: "${task}"`
    ]);

    const apiKey = import.meta.env.VITE_GEMINI_KEY;
    if (!apiKey) {
      setLogs(prev => [...prev, '❌ Error: VITE_GEMINI_KEY not found in .env']);
      setIsRunning(false);
      return;
    }

    try {
      const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=' + apiKey, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: task + '\n\nRespond clearly and concisely.' }] }]
        })
      });

      const data = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
      
      setLogs(prev => [...prev, `✅ Gemini: ${text}`]);
    } catch (error) {
      setLogs(prev => [...prev, `💥 Error: ${error.message}`]);
    }

    setIsRunning(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
        sentient-ui
      </h1>

      <div className="bg-white rounded-xl shadow-md p-6 mb-6">
        <input
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Ask Gemini anything... (e.g., Summarize quantum computing)"
          className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
          disabled={isRunning}
          onKeyPress={(e) => e.key === 'Enter' && runTask()}
        />
        <button
          onClick={runTask}
          disabled={isRunning}
          className="mt-4 w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition"
        >
          {isRunning ? '🧠 Thinking...' : '▶️ Activate Agent'}
        </button>
      </div>

      <div className="bg-gray-900 text-green-400 p-6 rounded-xl font-mono text-sm h-96 overflow-y-auto">
        <div className="space-y-2">
          {logs.length === 0 ? (
            <div className="text-gray-500">Awaiting task...</div>
          ) : (
            logs.map((log, i) => <div key={i}>{log}</div>
          ))}
        </div>
      </div>
    </div>
  );
}