import { useState } from 'react';
import { AgentRuntime } from '../agent/AgentRuntime';

export default function AgentDashboard() {
  const [task, setTask] = useState('');
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  const runTask = async () => {
    setIsRunning(true);
    setLogs(['Starting agent...']);

    const runtime = new AgentRuntime(import.meta.env.VITE_OPENAI_KEY);
    
    const result = await runtime.runTask(task, {
      onChainStart: (chain) => setLogs(prev => [...prev, `Starting: ${chain.name}`]),
      onAgentAction: (action) => setLogs(prev => [...prev, `Action: ${action.log}`]),
      onChainEnd: (output) => setLogs(prev => [...prev, `Done: ${output.text}`])
    });

    setIsRunning(false);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">sentient-ui</h1>
      
      <input
        value={task}
        onChange={(e) => setTask(e.target.value)}
        placeholder="e.g., Research best laptops under $1000"
        className="w-full p-3 border rounded mb-4"
        disabled={isRunning}
      />
      
      <button
        onClick={runTask}
        disabled={isRunning}
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {isRunning ? 'Running...' : 'Activate Agent'}
      </button>

      <div className="mt-6 p-4 border rounded h-96 overflow-y-auto font-mono text-sm">
        {logs.map((log, i) => (
          <div key={i} className="py-1 border-b border-gray-100">{log}</div>
        ))}
      </div>
    </div>
  );
}
const runTask = async () => {
  setIsRunning(true);
  setLogs(['🚀 Agent activated...']);

  const apiKey = import.meta.env.VITE_GEMINI_KEY;
  if (!apiKey) {
    setLogs(prev => [...prev, '❌ Error: Gemini key not found in .env']);
    return;
  }

  const runtime = new AgentRuntime(apiKey);
  setLogs(prev => [...prev, `🧠 Using Gemini 1.5 Pro`]);

  const result = await runtime.runTask(task);
  setLogs(prev => [...prev, `✅ ${result.output}`]);

  setIsRunning(false);
};