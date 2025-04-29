// import React from "react";

// export const Select = ({ children, ...props }) => (
//   <select {...props} className="w-full h-12 border rounded-lg px-4">
//     {children}
//   </select>
// );

// export const SelectTrigger = ({ children }) => <>{children}</>;

// export const SelectValue = ({ placeholder }) => (
//   <option value="">{placeholder}</option>
// );

// export const SelectContent = ({ children }) => <>{children}</>;

// export const SelectItem = ({ value, children }) => (
//   <option value={value}>{children}</option>
// );



import React from 'react';

export const Select = ({ value, onValueChange, children, placeholder }) => {
  return (
    <select
      value={value}
      onChange={(e) => onValueChange(e.target.value)}
      className="w-full h-12 px-4 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-emerald-500"
    >
      <option value="" disabled hidden>
        {placeholder || "Select an option"}
      </option>
      {children}
    </select>
  );
};

export const SelectTrigger = ({ children }) => {
  return <>{children}</>;
};

export const SelectValue = ({ placeholder }) => {
  return null; // Not needed since we are using native select's placeholder
};

export const SelectContent = ({ children }) => {
  return <>{children}</>;
};

export const SelectItem = ({ value, children }) => {
  return <option value={value}>{children}</option>;
};
