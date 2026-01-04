import React from 'react';

export const ShortcutsMenu = () => {
  return (
    <div className="absolute bottom-12 right-4 w-64 bg-white rounded-lg shadow-xl border border-slate-200 p-4 z-50 animate-in fade-in slide-in-from-bottom-2 duration-200">
      <h4 className="font-bold text-slate-900 mb-3 text-sm">Keyboard shortcuts</h4>
      
      <div className="space-y-3">
        <ShortcutRow label="Move through notifications" keys={['↓', '↑']} />
        <ShortcutRow label="Expand notification" keys={['e']} />
        <ShortcutRow label="Change read state" keys={['r']} />
        <ShortcutRow label="First notification" keys={['shift', '↑']} />
        <ShortcutRow label="Last notification" keys={['shift', '↓']} />
      </div>
    </div>
  );
};

const ShortcutRow = ({ label, keys }: { label: string, keys: string[] }) => (
  <div className="flex items-center justify-between text-xs">
    <span className="text-slate-600">{label}</span>
    <div className="flex items-center gap-1">
      {keys.map((k, i) => (
        <React.Fragment key={k}>
          {i > 0 && k !== '↑' && k !== '↓' && <span className="text-slate-400 mx-0.5">+</span>}
          <kbd className="bg-slate-100 border border-slate-300 rounded px-1.5 py-0.5 font-sans text-slate-500 min-w-[20px] text-center">
            {k === 'shift' ? 'shift' : k}
          </kbd>
        </React.Fragment>
      ))}
    </div>
  </div>
);