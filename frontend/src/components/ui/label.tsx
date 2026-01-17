import * as React from "react";

export interface LabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement> {}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className = "", ...props }, ref) => {
    const baseStyles =
      "text-sm font-medium text-gray-700 dark:text-gray-300 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70";

    return (
      <label
        ref={ref}
        className={`${baseStyles} ${className}`}
        {...props}
      />
    );
  }
);

Label.displayName = "Label";

export { Label };
