import { useState } from "react";

import type { CRMFieldMappingEntry } from "../../types";
import { Button } from "../ui/button";
import { Card } from "../ui/card";

type FieldMappingBuilderProps = {
  value: CRMFieldMappingEntry[];
  localFields: string[];
  remoteFields: string[];
  onChange: (mappings: CRMFieldMappingEntry[]) => void;
  title: string;
};

type DragData = {
  type: "local" | "remote";
  field: string;
};

export function FieldMappingBuilder({
  value,
  localFields,
  remoteFields,
  onChange,
  title,
}: FieldMappingBuilderProps) {
  const [lastDrag, setLastDrag] = useState<DragData | null>(null);

  const handleDrop = (index: number, type: "local" | "remote") => {
    if (!lastDrag || lastDrag.type !== type) return;
    const next = [...value];
    const entry = { ...next[index] };
    if (type === "local") {
      entry.local_field = lastDrag.field;
    } else {
      entry.remote_field = lastDrag.field;
    }
    next[index] = entry;
    onChange(next);
    setLastDrag(null);
  };

  const handleDragStart = (field: string, type: "local" | "remote") => {
    setLastDrag({ field, type });
  };

  const handleAddRow = () => {
    onChange([...value, { local_field: "", remote_field: "", transform: undefined }]);
  };

  const handleRemoveRow = (index: number) => {
    const next = [...value];
    next.splice(index, 1);
    onChange(next);
  };

  const handleTransformChange = (index: number, transform: string) => {
    const next = [...value];
    next[index] = { ...next[index], transform: transform || undefined };
    onChange(next);
  };

  return (
    <Card className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold">{title}</h4>
        <Button size="sm" variant="outline" onClick={handleAddRow}>
          Add Mapping
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Our Fields
          </h5>
          <div className="space-y-2 rounded-md border border-dashed p-3">
            {localFields.map((field) => (
              <div
                key={field}
                className="cursor-grab rounded border bg-slate-50 px-2 py-1 text-sm text-slate-700"
                draggable
                onDragStart={() => handleDragStart(field, "local")}
              >
                {field}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h5 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            CRM Fields
          </h5>
          <div className="space-y-2 rounded-md border border-dashed p-3">
            {remoteFields.map((field) => (
              <div
                key={field}
                className="cursor-grab rounded border bg-slate-50 px-2 py-1 text-sm text-slate-700"
                draggable
                onDragStart={() => handleDragStart(field, "remote")}
              >
                {field}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {value.length === 0 ? (
          <p className="text-sm text-muted-foreground">No mappings configured yet.</p>
        ) : (
          value.map((entry, index) => (
            <div
              key={`${entry.local_field}-${entry.remote_field}-${index}`}
              className="flex flex-col gap-3 rounded-md border p-3 md:flex-row md:items-center md:justify-between"
            >
              <div className="flex flex-1 flex-col gap-3 md:flex-row md:items-center md:gap-4">
                <div
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={() => handleDrop(index, "local")}
                  className="flex min-h-[48px] flex-1 items-center justify-between rounded border border-dashed px-3 py-2 text-sm"
                >
                  <span className="text-xs font-medium uppercase text-slate-500">Local</span>
                  <span className="font-semibold text-slate-700">
                    {entry.local_field || <em className="text-slate-400">Drop field</em>}
                  </span>
                </div>
                <div
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={() => handleDrop(index, "remote")}
                  className="flex min-h-[48px] flex-1 items-center justify-between rounded border border-dashed px-3 py-2 text-sm"
                >
                  <span className="text-xs font-medium uppercase text-slate-500">CRM</span>
                  <span className="font-semibold text-slate-700">
                    {entry.remote_field || <em className="text-slate-400">Drop field</em>}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <input
                  className="w-40 rounded border px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
                  placeholder="Transform (optional)"
                  value={entry.transform ?? ""}
                  onChange={(event) => handleTransformChange(index, event.target.value)}
                />
                <Button variant="ghost" size="sm" onClick={() => handleRemoveRow(index)}>
                  Remove
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}

