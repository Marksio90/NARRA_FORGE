"use client";

import * as React from "react";

export interface DropdownMenuProps {
  children: React.ReactNode;
}

export function DropdownMenu({ children }: DropdownMenuProps) {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="relative inline-block text-left">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            open,
            setOpen,
          });
        }
        return child;
      })}
    </div>
  );
}

export interface DropdownMenuTriggerProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  open?: boolean;
  setOpen?: (open: boolean) => void;
  asChild?: boolean;
}

export function DropdownMenuTrigger({
  children,
  open,
  setOpen,
  asChild,
  ...props
}: DropdownMenuTriggerProps) {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<any>, {
      onClick: () => setOpen?.(!open),
    });
  }

  return (
    <button onClick={() => setOpen?.(!open)} {...props}>
      {children}
    </button>
  );
}

export interface DropdownMenuContentProps
  extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean;
  setOpen?: (open: boolean) => void;
  align?: "start" | "center" | "end";
}

export function DropdownMenuContent({
  children,
  className = "",
  open,
  setOpen,
  align = "end",
  ...props
}: DropdownMenuContentProps) {
  if (!open) return null;

  const alignmentClasses = {
    start: "left-0",
    center: "left-1/2 -translate-x-1/2",
    end: "right-0",
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40"
        onClick={() => setOpen?.(false)}
      />

      {/* Dropdown Content */}
      <div
        className={`absolute ${alignmentClasses[align]} mt-2 z-50 min-w-[8rem] overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg ${className}`}
        {...props}
      >
        {children}
      </div>
    </>
  );
}

export interface DropdownMenuItemProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  destructive?: boolean;
}

export function DropdownMenuItem({
  className = "",
  destructive,
  children,
  ...props
}: DropdownMenuItemProps) {
  const baseStyles =
    "relative flex cursor-pointer select-none items-center px-3 py-2 text-sm outline-none transition-colors hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left";

  const destructiveStyles = destructive
    ? "text-red-600 dark:text-red-400"
    : "text-gray-900 dark:text-gray-100";

  return (
    <button
      className={`${baseStyles} ${destructiveStyles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export interface DropdownMenuSeparatorProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function DropdownMenuSeparator({
  className = "",
  ...props
}: DropdownMenuSeparatorProps) {
  return (
    <div
      className={`-mx-1 my-1 h-px bg-gray-200 dark:bg-gray-700 ${className}`}
      {...props}
    />
  );
}

export interface DropdownMenuLabelProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function DropdownMenuLabel({
  className = "",
  children,
  ...props
}: DropdownMenuLabelProps) {
  return (
    <div
      className={`px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
