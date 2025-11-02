import * as React from "react";
import { clsx } from "clsx";

interface SelectContextValue {
  value: string;
  onValueChange: (value: string) => void;
}

const SelectContext = React.createContext<SelectContextValue | undefined>(undefined);

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
}

export function Select({ value, onValueChange, children }: SelectProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const selectRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  return (
    <SelectContext.Provider value={{ value, onValueChange }}>
      <div ref={selectRef} className="relative">
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child, { isOpen, setIsOpen } as any);
          }
          return child;
        })}
      </div>
    </SelectContext.Provider>
  );
}

interface SelectTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isOpen?: boolean;
  setIsOpen?: (open: boolean) => void;
}

export const SelectTrigger = React.forwardRef<HTMLButtonElement, SelectTriggerProps>(
  ({ className, children, isOpen, setIsOpen, ...props }, ref) => {
    const context = React.useContext(SelectContext);
    if (!context) throw new Error("SelectTrigger must be used within Select");

    return (
      <button
        ref={ref}
        type="button"
        onClick={() => setIsOpen?.(!isOpen)}
        className={clsx(
          "flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        {...props}
      >
        {children}
        <span className="ml-2">▼</span>
      </button>
    );
  }
);

SelectTrigger.displayName = "SelectTrigger";

interface SelectValueProps {
  placeholder?: string;
}

export function SelectValue({ placeholder = "Select..." }: SelectValueProps) {
  const context = React.useContext(SelectContext);
  if (!context) throw new Error("SelectValue must be used within Select");

  return <span>{context.value || placeholder}</span>;
}

interface SelectContentProps extends React.HTMLAttributes<HTMLDivElement> {
  isOpen?: boolean;
}

export const SelectContent = React.forwardRef<HTMLDivElement, SelectContentProps>(
  ({ className, children, isOpen, ...props }, ref) => {
    if (!isOpen) return null;

    return (
      <div
        ref={ref}
        className={clsx(
          "absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border border-gray-200 bg-white shadow-lg",
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

SelectContent.displayName = "SelectContent";

interface SelectItemProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export function SelectItem({ value, className, children, ...props }: SelectItemProps) {
  const context = React.useContext(SelectContext);
  if (!context) throw new Error("SelectItem must be used within Select");

  const isSelected = context.value === value;

  return (
    <div
      className={clsx(
        "cursor-pointer px-3 py-2 text-sm hover:bg-gray-100",
        isSelected && "bg-blue-50",
        className
      )}
      onClick={() => {
        context.onValueChange(value);
      }}
      {...props}
    >
      {children}
    </div>
  );
}

