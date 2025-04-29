import React from "react";

export const Table = ({ children }) => (
  <table className="min-w-full bg-white border rounded-lg">
    {children}
  </table>
);

export const TableHeader = ({ children }) => (
  <thead className="bg-gray-100">{children}</thead>
);

export const TableBody = ({ children }) => <tbody>{children}</tbody>;

export const TableRow = ({ children }) => <tr>{children}</tr>;

export const TableHead = ({ children }) => (
  <th className="py-2 px-4 border">{children}</th>
);

export const TableCell = ({ children }) => (
  <td className="py-2 px-4 border">{children}</td>
);
