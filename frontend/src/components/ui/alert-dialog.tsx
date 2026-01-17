"use client";

import * as React from "react";
import { Button } from "./button";

export interface AlertDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export function AlertDialog({ open, onOpenChange, children }: AlertDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />

      {/* Alert Dialog Content */}
      <div className="relative z-50">{children}</div>
    </div>
  );
}

export interface AlertDialogContentProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function AlertDialogContent({
  className = "",
  children,
  ...props
}: AlertDialogContentProps) {
  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 w-full max-w-md ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export interface AlertDialogHeaderProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function AlertDialogHeader({
  className = "",
  children,
  ...props
}: AlertDialogHeaderProps) {
  return (
    <div
      className={`flex flex-col space-y-2 text-center sm:text-left mb-4 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export interface AlertDialogTitleProps
  extends React.HTMLAttributes<HTMLHeadingElement> {}

export function AlertDialogTitle({
  className = "",
  children,
  ...props
}: AlertDialogTitleProps) {
  return (
    <h2
      className={`text-lg font-semibold text-gray-900 dark:text-white ${className}`}
      {...props}
    >
      {children}
    </h2>
  );
}

export interface AlertDialogDescriptionProps
  extends React.HTMLAttributes<HTMLParagraphElement> {}

export function AlertDialogDescription({
  className = "",
  children,
  ...props
}: AlertDialogDescriptionProps) {
  return (
    <p
      className={`text-sm text-gray-600 dark:text-gray-400 ${className}`}
      {...props}
    >
      {children}
    </p>
  );
}

export interface AlertDialogFooterProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function AlertDialogFooter({
  className = "",
  children,
  ...props
}: AlertDialogFooterProps) {
  return (
    <div
      className={`flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 mt-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export interface AlertDialogActionProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export function AlertDialogAction({
  className = "",
  children,
  ...props
}: AlertDialogActionProps) {
  return (
    <Button className={className} {...props}>
      {children}
    </Button>
  );
}

export interface AlertDialogCancelProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export function AlertDialogCancel({
  className = "",
  children,
  ...props
}: AlertDialogCancelProps) {
  return (
    <Button variant="outline" className={className} {...props}>
      {children}
    </Button>
  );
}
